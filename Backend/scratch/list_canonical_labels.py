import os
import psycopg2

db_url = os.environ.get("DATABASE_URL", "postgresql://tracex:tracex_dev_password@localhost:5432/tracex")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("""
        SELECT canonical_label, COUNT(*) 
        FROM canonical_node_records 
        GROUP BY canonical_label
    """)
    print("Canonical Labels:", cur.fetchall())
except Exception as e:
    print("DB Error:", e)
