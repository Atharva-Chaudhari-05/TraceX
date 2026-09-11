import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.app.analytics.ml_engine import MLEngine
from backend.app.core.postgres import SessionLocal

db = SessionLocal()
try:
    engine = MLEngine()
    result = engine.train_models(["CASE-SMOKE-POS", "CASE-SMOKE-NEG"])
    print("SUCCESS", result)
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()
