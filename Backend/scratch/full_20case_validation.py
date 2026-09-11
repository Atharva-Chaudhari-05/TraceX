"""
Full 20-case validation against live PostgreSQL + Neo4j + backend APIs.
"""
import psycopg2
import httpx
import json
from neo4j import GraphDatabase

CASES = [
    "CASE-01591", "CASE-00394", "CASE-01744", "CASE-00184", "CASE-00529",
    "CASE-00959", "CASE-01084", "CASE-01664", "CASE-00564", "CASE-01209",
    "CASE-01334", "CASE-01594", "CASE-00349", "CASE-01269", "CASE-01994",
    "CASE-00139", "CASE-01519", "CASE-01124", "CASE-01059", "CASE-01584",
]

print("=" * 60)
print("TRACE-X 20-CASE FULL VALIDATION")
print("=" * 60)

# 1. PostgreSQL verification
print("\n[1] POSTGRESQL VERIFICATION")
conn = psycopg2.connect('postgresql://tracex:tracex_dev_password@localhost:5432/tracex')
cur = conn.cursor()
cur.execute("SELECT canonical_label, COUNT(*) FROM canonical_node_records GROUP BY canonical_label ORDER BY canonical_label")
print("  Node counts by label:")
for r in cur.fetchall():
    print(f"    {r[0]}: {r[1]}")

cur.execute("SELECT canonical_id FROM canonical_node_records WHERE canonical_label = 'Case' ORDER BY canonical_id")
pg_cases = [r[0] for r in cur.fetchall()]
print(f"\n  Case nodes found in PostgreSQL: {len(pg_cases)}/20")
missing_pg = set(CASES) - set(pg_cases)
if missing_pg:
    print(f"  MISSING: {sorted(missing_pg)}")
else:
    print("  All 20 cases PRESENT in PostgreSQL ✓")

cur.execute("SELECT COUNT(*) FROM canonical_relationship_records")
rel_count = cur.fetchone()[0]
print(f"  Relationships in PostgreSQL: {rel_count}")

# 2. Neo4j verification
print("\n[2] NEO4J VERIFICATION")
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'tracex_dev_password'))
with driver.session() as s:
    r = s.run('MATCH (n) RETURN count(n) as cnt')
    total_nodes = r.single()['cnt']
    r = s.run('MATCH ()-[r]->() RETURN count(r) as cnt')
    total_rels = r.single()['cnt']
    print(f"  Total Neo4j nodes: {total_nodes}")
    print(f"  Total Neo4j relationships: {total_rels}")
    
    r = s.run('MATCH (n) WHERE n.id IN $ids RETURN n.id ORDER BY n.id', ids=CASES)
    neo4j_cases = [row['n.id'] for row in r.data()]
    print(f"\n  Case nodes found in Neo4j: {len(neo4j_cases)}/20")
    missing_neo = set(CASES) - set(neo4j_cases)
    if missing_neo:
        print(f"  MISSING: {sorted(missing_neo)}")
    else:
        print("  All 20 cases PRESENT in Neo4j ✓")
    
    # Per-case neighborhood check for 3 representative cases
    print("\n  Per-case neighborhood check (sample 3):")
    for case_id in ["CASE-01591", "CASE-00394", "CASE-01209"]:
        r = s.run(
            'MATCH (n {id: $cid})-[rel]-(m) RETURN count(DISTINCT m) as nb, count(DISTINCT rel) as nr',
            cid=case_id
        )
        row = r.single()
        nb = row['nb'] if row else 0
        nr = row['nr'] if row else 0
        status = "✓" if nb > 0 else "✗"
        print(f"    {case_id}: {nb} neighbors, {nr} relationships {status}")

driver.close()

# 3. API verification
print("\n[3] BACKEND API VERIFICATION")
base_url = "http://localhost:8000/api/v1"
token = None
try:
    res = httpx.post(f"{base_url}/auth/login", json={"email": "admin@tracex.local", "password": "adminpassword"})
    if res.status_code == 200:
        token = res.json().get("access_token")
        print("  Auth: 200 OK ✓")
    else:
        print(f"  Auth: FAILED {res.status_code}")
except Exception as e:
    print(f"  Auth: ERROR {e}")

results = {}
if token:
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 3 cases through graph endpoint
    for case_id in ["CASE-01591", "CASE-00394", "CASE-01209"]:
        try:
            r = httpx.get(f"{base_url}/graph/neighborhood/{case_id}", headers=headers, timeout=15)
            nodes = len(r.json().get('nodes', [])) if r.status_code == 200 else 0
            results[f"graph_{case_id}"] = f"{r.status_code} ({nodes} nodes)"
            print(f"  Graph {case_id}: {r.status_code} - {nodes} nodes")
        except Exception as e:
            print(f"  Graph {case_id}: ERROR {e}")
    
    # Analytics
    try:
        r = httpx.get(f"{base_url}/analytics/network?case_id=CASE-01591", headers=headers, timeout=15)
        results["analytics"] = str(r.status_code)
        print(f"  Analytics (CASE-01591): {r.status_code}")
        if r.status_code == 200:
            body = r.json()
            print(f"    nodes={body.get('node_count', 0)}, entities={len(body.get('key_entities', []))}, communities={len(body.get('communities', []))}")
    except Exception as e:
        print(f"  Analytics: ERROR {e}")
    
    # ML
    try:
        r = httpx.get(f"{base_url}/ml/case/CASE-01591/signals", headers=headers, timeout=30)
        results["ml"] = str(r.status_code)
        print(f"  ML Signals (CASE-01591): {r.status_code}")
        if r.status_code == 200:
            print(f"    signals={len(r.json().get('signals', []))}")
    except Exception as e:
        print(f"  ML: ERROR {e}")

print("\n[4] 20-CASE SUMMARY")
print(f"  PostgreSQL cases: {len(pg_cases)}/20")
print(f"  Neo4j cases: {len(neo4j_cases)}/20")
pg_pass = len(pg_cases) == 20 and len(missing_pg) == 0
neo_pass = len(neo4j_cases) == 20 and len(missing_neo) == 0
print(f"  PostgreSQL PASS: {pg_pass}")
print(f"  Neo4j PASS: {neo_pass}")
print(f"  Overall: {'PASS ✓' if pg_pass and neo_pass else 'PARTIAL — see above'}")
print("\n" + "=" * 60)
conn.close()
