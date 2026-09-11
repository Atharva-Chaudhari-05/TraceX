import sys
import os
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.app.core.postgres import SessionLocal

with SessionLocal() as db:
    queries = db.execute(text("SELECT state, query FROM pg_stat_activity WHERE datname = 'tracex_prepared_test' AND state IN ('active', 'idle in transaction')")).fetchall()
    for q in queries:
        print(f"[{q[0]}] {q[1][:200]}")
