"""
Remove only the demo_a_20cases batch records created today
so the idempotency guard allows re-ingestion with the fixed engine.
Does NOT touch the 7-CSV Demo B batches (from 9:40 UTC today).
"""
import psycopg2
from datetime import datetime, timezone

conn = psycopg2.connect('postgresql://tracex:tracex_dev_password@localhost:5432/tracex')
cur = conn.cursor()

# Find batches created in the demo_a_20cases run (started ~11:24 UTC)
cur.execute("""
  SELECT id, file_name, status, valid_records, started_at
  FROM ingestion_batches
  WHERE started_at > '2026-09-11 11:20:00+00'
  ORDER BY started_at
""")
rows = cur.fetchall()
print("Batches to remove:")
ids_to_remove = []
for r in rows:
    print(f"  {r[1]} | {r[2]} | valid={r[3]} | started={r[4]}")
    ids_to_remove.append(str(r[0]))

if ids_to_remove:
    # Delete error logs first (FK constraint)
    cur.execute("DELETE FROM ingestion_error_logs WHERE batch_id = ANY(%s::uuid[])", (ids_to_remove,))
    # Delete canonical records associated with these batches (should be 0 but safety)
    cur.execute("DELETE FROM canonical_node_records WHERE batch_id = ANY(%s::uuid[])", (ids_to_remove,))
    cur.execute("DELETE FROM canonical_relationship_records WHERE batch_id = ANY(%s::uuid[])", (ids_to_remove,))
    # Delete batches
    cur.execute("DELETE FROM ingestion_batches WHERE id = ANY(%s::uuid[])", (ids_to_remove,))
    conn.commit()
    print(f"\nRemoved {len(ids_to_remove)} batches. Ready for clean re-ingestion.")
else:
    print("No matching batches found.")

conn.close()
