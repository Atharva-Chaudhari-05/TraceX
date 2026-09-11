import psycopg2
conn = psycopg2.connect('postgresql://tracex:tracex_dev_password@localhost:5432/tracex')
cur = conn.cursor()

# Find the specific rel + org batches from the last run
cur.execute("""
  SELECT id, file_name, status, valid_records, started_at
  FROM ingestion_batches
  WHERE started_at > '2026-09-11 11:26:00+00'
    AND file_name IN ('relationships.csv', 'organizations.csv')
  ORDER BY started_at
""")
rows = cur.fetchall()
print("Batches to remove:")
ids_to_remove = []
for r in rows:
    print(f"  {r[1]} | {r[2]} | valid={r[3]}")
    ids_to_remove.append(str(r[0]))

if ids_to_remove:
    cur.execute("DELETE FROM ingestion_error_logs WHERE batch_id = ANY(%s::uuid[])", (ids_to_remove,))
    cur.execute("DELETE FROM canonical_node_records WHERE batch_id = ANY(%s::uuid[])", (ids_to_remove,))
    cur.execute("DELETE FROM canonical_relationship_records WHERE batch_id = ANY(%s::uuid[])", (ids_to_remove,))
    cur.execute("DELETE FROM ingestion_batches WHERE id = ANY(%s::uuid[])", (ids_to_remove,))
    conn.commit()
    print(f"Removed {len(ids_to_remove)} batches.")
else:
    print("No matching batches.")
conn.close()
