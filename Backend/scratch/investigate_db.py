import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.postgres import SessionLocal, engine
from sqlalchemy import text

def inspect_db():
    print("=" * 70)
    print("DB Inspection")
    print("=" * 70)
    
    url = engine.url
    print(f"Target Host: {url.host}")
    print(f"Target Port: {url.port}")
    print(f"Target Database: {url.database}")
    print(f"Target User: {url.username}")
    
    with SessionLocal() as db:
        current_db = db.execute(text("SELECT current_database();")).scalar()
        print(f"\nCurrent Database from SQL: {current_db}")
        
        try:
            batch_count = db.execute(text("SELECT COUNT(*) FROM ingestion_batches;")).scalar()
            print(f"ingestion_batches COUNT: {batch_count}")
        except Exception as e:
            print(f"ingestion_batches COUNT: ERROR - {e}")
            
        try:
            nodes_count = db.execute(text("SELECT COUNT(*) FROM canonical_node_records;")).scalar()
            print(f"canonical_node_records COUNT: {nodes_count}")
        except Exception as e:
            print(f"canonical_node_records COUNT: ERROR - {e}")
            
        try:
            rel_count = db.execute(text("SELECT COUNT(*) FROM canonical_relationship_records;")).scalar()
            print(f"canonical_relationship_records COUNT: {rel_count}")
        except Exception as e:
            print(f"canonical_relationship_records COUNT: ERROR - {e}")
            
        try:
            print("Batch Statuses:")
            statuses = db.execute(text("SELECT status, COUNT(*) FROM ingestion_batches GROUP BY status ORDER BY status;")).fetchall()
            for s in statuses:
                print(f"  {s[0]}: {s[1]}")
        except Exception as e:
            print(f"Batch Statuses: ERROR - {e}")

if __name__ == "__main__":
    inspect_db()
