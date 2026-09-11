from backend.app.core.postgres import engine
from sqlalchemy import text

def run():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT tgname, pg_get_triggerdef(oid) FROM pg_trigger WHERE tgname LIKE '%audit%'")).fetchall()
        print("Triggers:", res)

if __name__ == "__main__":
    run()
