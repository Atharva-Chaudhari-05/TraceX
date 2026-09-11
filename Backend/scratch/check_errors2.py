import psycopg2
conn = psycopg2.connect('postgresql://tracex:tracex_dev_password@localhost:5432/tracex')
cur = conn.cursor()
cur.execute("""
  SELECT b.file_name, e.error_message
  FROM ingestion_batches b
  JOIN ingestion_error_logs e ON e.batch_id = b.id
  WHERE b.started_at > '2026-09-11 11:26:00+00'
    AND b.file_name IN ('relationships.csv', 'organizations.csv')
  LIMIT 5
""")
rows = cur.fetchall()
for r in rows:
    print('FILE:', r[0])
    print('ERROR:', str(r[1])[:400])
    print()

# Also check case count
cur.execute("SELECT canonical_label, COUNT(*) FROM canonical_node_records GROUP BY canonical_label ORDER BY canonical_label")
print("NODE COUNTS:")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]}")
    
cur.execute("SELECT COUNT(*) FROM canonical_node_records WHERE canonical_id LIKE 'CASE-%'")
print("Case-ID nodes:", cur.fetchone()[0])
