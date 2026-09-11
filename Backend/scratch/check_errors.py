import psycopg2
conn = psycopg2.connect('postgresql://tracex:tracex_dev_password@localhost:5432/tracex')
cur = conn.cursor()
cur.execute("""
  SELECT b.file_name, b.id, e.error_message, e.raw_data 
  FROM ingestion_batches b
  JOIN ingestion_error_logs e ON e.batch_id = b.id
  WHERE b.started_at > NOW() - INTERVAL '2 hours'
  LIMIT 5
""")
rows = cur.fetchall()
for r in rows:
    print('FILE:', r[0])
    print('ERROR:', str(r[2])[:300])
    print('DATA:', str(r[3])[:200])
    print()
