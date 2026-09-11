import psycopg2
conn = psycopg2.connect("dbname=tracex user=tracex password=tracex_dev_password host=localhost port=5432")
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
tables = [r[0] for r in cur.fetchall()]
print('Tables:', tables)

cur.execute("SELECT name FROM roles")
roles = [r[0] for r in cur.fetchall()]
print('Roles:', roles)

cur.close()
conn.close()
