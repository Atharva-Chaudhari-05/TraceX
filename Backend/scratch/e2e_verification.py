"""
Full E2E API verification for Demo A (20 cases) and Demo B (7-CSV).
"""
import httpx
import json
import psycopg2
from neo4j import GraphDatabase

BASE = "http://localhost:8000/api/v1"

DEMO_A_CASES = [
    "CASE-01591", "CASE-00394", "CASE-01744", "CASE-00184", "CASE-00529",
    "CASE-00959", "CASE-01084", "CASE-01664", "CASE-00564", "CASE-01209",
    "CASE-01334", "CASE-01594", "CASE-00349", "CASE-01269", "CASE-01994",
    "CASE-00139", "CASE-01519", "CASE-01124", "CASE-01059", "CASE-01584",
]

print("=" * 70)
print("TRACE-X FINAL E2E VERIFICATION")
print("=" * 70)

# Auth
res = httpx.post(f"{BASE}/auth/login", json={"email": "admin@tracex.local", "password": "adminpassword"})
assert res.status_code == 200, f"Login failed: {res.status_code} {res.text}"
token = res.json()["access_token"]
H = {"Authorization": f"Bearer {token}"}
print(f"\n[AUTH] Login: 200 OK ✓")

# =====================================================================
print("\n" + "=" * 70)
print("DEMO A — 20-CASE PRELOADED INVESTIGATIONS")
print("=" * 70)

# Spot check 3 representative cases through full flow
for case_id in ["CASE-01591", "CASE-00394", "CASE-01209"]:
    print(f"\n  --- {case_id} ---")

    # Graph
    r = httpx.get(f"{BASE}/graph/neighborhood/{case_id}", headers=H, timeout=20)
    nodes = r.json().get("nodes", []) if r.status_code == 200 else []
    edges = r.json().get("edges", []) if r.status_code == 200 else []
    print(f"  Graph:     {r.status_code} | nodes={len(nodes)} edges={len(edges)}")

    # Analytics
    r = httpx.get(f"{BASE}/analytics/network?case_id={case_id}", headers=H, timeout=20)
    if r.status_code == 200:
        body = r.json()
        print(f"  Analytics: 200 | node_count={body.get('node_count')} key_entities={len(body.get('key_entities',[]))} communities={len(body.get('communities',[]))}")
    else:
        print(f"  Analytics: {r.status_code} | {r.text[:120]}")

    # ML
    r = httpx.get(f"{BASE}/ml/case/{case_id}/signals", headers=H, timeout=30)
    if r.status_code == 200:
        sigs = r.json().get("signals", [])
        print(f"  ML:        200 | signals={len(sigs)}")
    else:
        print(f"  ML:        {r.status_code} | {r.text[:120]}")

# All 20 cases graph check
print(f"\n  All 20 cases graph check:")
passed = 0
for case_id in DEMO_A_CASES:
    r = httpx.get(f"{BASE}/graph/neighborhood/{case_id}", headers=H, timeout=20)
    n = len(r.json().get("nodes", [])) if r.status_code == 200 else 0
    ok = r.status_code == 200 and n > 0
    if ok:
        passed += 1
    else:
        print(f"    ✗ {case_id}: {r.status_code}, nodes={n}")
print(f"  Graph: {passed}/20 cases returning live nodes ✓" if passed == 20 else f"  Graph: {passed}/20 ← PARTIAL")

# =====================================================================
print("\n" + "=" * 70)
print("DEMO B — 7-CSV PIPELINE")
print("=" * 70)

# Check Demo B data is still intact in PostgreSQL
conn = psycopg2.connect('postgresql://tracex:tracex_dev_password@localhost:5432/tracex')
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM ingestion_batches WHERE started_at < '2026-09-11 11:20:00+00'")
demo_b_batches = cur.fetchone()[0]
print(f"\n  Demo B ingestion batches preserved: {demo_b_batches}")

cur.execute("""
    SELECT canonical_label, COUNT(*) 
    FROM canonical_node_records cnr
    JOIN ingestion_batches ib ON cnr.batch_id = ib.id
    WHERE ib.started_at < '2026-09-11 11:20:00+00'
    GROUP BY canonical_label
""")
print("  Demo B node counts (from early batches):")
for r in cur.fetchall():
    print(f"    {r[0]}: {r[1]}")
conn.close()

# Demo B person node available in Neo4j — check a real person
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'tracex_dev_password'))
with driver.session() as s:
    r = s.run("MATCH (n:Person) RETURN n.id LIMIT 3")
    persons = [row['n.id'] for row in r.data()]
    print(f"\n  Demo B sample person nodes in Neo4j: {persons}")
    
    if persons:
        pid = persons[0]
        r = s.run("MATCH (n {id: $pid})-[rel]-(m) RETURN count(DISTINCT m) as nb", pid=pid)
        nb = r.single()['nb']
        print(f"  Neighborhood of {pid}: {nb} neighbors")
driver.close()

# Test ingestion API
r = httpx.get(f"{BASE}/ingestion/batches", headers=H, timeout=10)
print(f"\n  Ingestion batches API: {r.status_code}")
if r.status_code == 200:
    batches = r.json() if isinstance(r.json(), list) else r.json().get("data", r.json().get("items", []))
    print(f"  Total batches visible: {len(batches) if isinstance(batches, list) else 'see response'}")

# =====================================================================
print("\n" + "=" * 70)
print("MOCK FALLBACK AUDIT")
print("=" * 70)

# Test graph endpoint with real entity IDs to confirm no mock
r = httpx.get(f"{BASE}/graph/neighborhood/CASE-01591", headers=H, timeout=20)
body = r.json()
nodes = body.get("nodes", [])
# Check if any node IDs look like real CASE-/PER- IDs vs mock "node-1" etc
real_ids = [n for n in nodes if any(n.get("id","").startswith(p) for p in ["CASE-","PER-","ACC-","TXN-","PAE-","INC-","DOC-","DEV-","LOC-","ORG-","PHO-","VEH-","PHYS-"])]
mock_ids = [n for n in nodes if n.get("id","").startswith("node-") or n.get("id","") == ""]
print(f"\n  CASE-01591 graph nodes: {len(nodes)} total")
print(f"  Real canonical IDs: {len(real_ids)}")
print(f"  Mock/empty IDs:     {len(mock_ids)}")
print(f"  Sample real IDs: {[n.get('id') for n in real_ids[:5]]}")

# Check analytics response for real case_id echo
r = httpx.get(f"{BASE}/analytics/network?case_id=CASE-01591", headers=H, timeout=20)
if r.status_code == 200:
    body = r.json()
    print(f"\n  Analytics case_id echo: '{body.get('case_id')}' (should be CASE-01591)")
    entities = body.get("key_entities", [])
    if entities:
        sample = entities[0]
        eid = sample.get("entity_id","") if isinstance(sample, dict) else getattr(sample, "entity_id","")
        print(f"  Sample key entity ID: '{eid}'")
        is_mock = eid.startswith("node-") or not eid
        print(f"  Mock entity IDs: {'YES — FALLBACK ACTIVE' if is_mock else 'NO — real IDs ✓'}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
