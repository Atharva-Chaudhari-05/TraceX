import psycopg2
conn = psycopg2.connect('postgresql://tracex:tracex_dev_password@localhost:5432/tracex')
cur = conn.cursor()

# Check total relationship records from Demo B batches (early ones before the 20-case ingest)
cur.execute("""
  SELECT COUNT(*) FROM canonical_relationship_records cr
  JOIN ingestion_batches ib ON cr.batch_id = ib.id
  WHERE ib.started_at < '2026-09-11 11:20:00+00'
""")
print('Total Demo B relationship records:', cur.fetchone()[0])

# Check total rels from Demo A 20-case
cur.execute("""
  SELECT COUNT(*) FROM canonical_relationship_records cr
  JOIN ingestion_batches ib ON cr.batch_id = ib.id
  WHERE ib.started_at >= '2026-09-11 11:20:00+00'
""")
print('Total Demo A relationship records:', cur.fetchone()[0])

# Check ingestion API route
import httpx
r = httpx.get("http://localhost:8000/api/v1/ingestion/batches", headers={"Authorization": "Bearer dummy"})
print("Ingestion batches API:", r.status_code)

# Check actual routes available
r2 = httpx.get("http://localhost:8000/openapi.json")
import json
routes = [r['path'] for r in r2.json().get('paths', {}).keys()]
ingestion_routes = [r for r in routes if 'ingestion' in r]
print("Ingestion routes available:", ingestion_routes)

conn.close()
