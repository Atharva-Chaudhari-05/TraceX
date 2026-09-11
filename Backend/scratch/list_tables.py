import os
import psycopg2
import json

db_url = os.environ.get("DATABASE_URL", "postgresql://tracex:tracex_dev_password@localhost:5432/tracex")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cur.fetchall()
    print("Tables:", tables)

    for (table,) in tables:
        cur.execute(f"SELECT count(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"Table {table}: {count} rows")
except Exception as e:
    print("DB Error:", e)
