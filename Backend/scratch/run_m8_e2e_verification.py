import json
import logging
from pathlib import Path
from backend.app.analytics.ml_engine import MLEngine
from backend.app.analytics.model_registry import ModelRegistry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEMO_20_CASES = [
    "CASE-01591", "CASE-00394", "CASE-01744", "CASE-00184",
    "CASE-00529", "CASE-00959", "CASE-01084", "CASE-01664",
    "CASE-00564", "CASE-01209", "CASE-01334", "CASE-01594",
    "CASE-00349", "CASE-01269", "CASE-01994", "CASE-00139",
    "CASE-01519", "CASE-01124", "CASE-01059", "CASE-01584",
]

def verify_dict_approx_equal(d1, d2):
    assert d1.keys() == d2.keys()
    for k in d1:
        v1, v2 = d1[k], d2[k]
        if isinstance(v1, float):
            assert abs(v1 - v2) < 1e-6
        else:
            assert v1 == v2

def main():
    engine = MLEngine()
    registry = engine.registry
    base_dir = Path(registry.base_dir)

    print("\n--- 5. TRAINING ---")
    res1 = engine.train_models(DEMO_20_CASES)
    print("Train result:", json.dumps(res1, indent=2))
    assert res1["status"] == "success"
    v1_xgb = res1["xgboost_version"]
    v1_iso = res1["isolation_forest_version"]

    assert (base_dir / "xgboost" / v1_xgb / "model.json").exists()
    assert (base_dir / "isolation_forest" / v1_iso / "model.joblib").exists()
    assert (base_dir / "isolation_forest" / v1_iso / "scaler.joblib").exists()

    with open(base_dir / "xgboost" / v1_xgb / "metadata.json") as f:
        meta1 = json.load(f)
        assert meta1["feature_schema_version"] == "1.0"
        print("XGB Metadata:", {k: v for k, v in meta1.items() if k != "metrics"})

    print("\n--- 8. 20-CASE INFERENCE (First run) ---")
    signals_first_run = {}
    for case_id in DEMO_20_CASES:
        res = engine.infer_case(case_id)
        signals = res["signals"]
        signals_first_run[case_id] = signals
        print(f"[{case_id}] Signals count: {len(signals)}")
        for sig in signals:
            assert sig["feature_values"], "Missing feature_values"
            assert sig["explanation"], "Missing explanation"
            assert sig["top_features"] is not None, "Missing top_features"
            assert "NaN" not in str(sig["feature_values"])
            assert "criminal" not in sig["explanation"].lower().replace("not real-world criminal", "")

    print("\n--- 6. RELOAD TEST ---")
    engine2 = MLEngine()
    engine2.registry = ModelRegistry()
    xgb_model, xgb_meta = engine2.registry.load_xgboost_model()
    iso_model, iso_scaler, iso_meta = engine2.registry.load_isolation_forest_model()
    print(f"Reloaded XGB version: {xgb_meta['model_version']}")
    print(f"Reloaded ISO version: {iso_meta['model_version']}")

    res_reload = engine2.infer_case(DEMO_20_CASES[0])
    s1 = signals_first_run[DEMO_20_CASES[0]][0]
    s2 = res_reload["signals"][0]
    verify_dict_approx_equal(s1["feature_values"], s2["feature_values"])
    assert s1["explanation"] == s2["explanation"]
    print("Reload inference structurally identical.")

    print("\n--- 7. VERSION TEST (Second training) ---")
    res2 = engine.train_models(DEMO_20_CASES)
    v2_xgb = res2["xgboost_version"]
    v2_iso = res2["isolation_forest_version"]
    print(f"Train 2 XGB version: {v2_xgb}")
    print(f"Train 2 ISO version: {v2_iso}")
    assert v2_xgb != v1_xgb
    assert v2_iso != v1_iso
    assert (base_dir / "xgboost" / v2_xgb / "model.json").exists()
    assert (base_dir / "xgboost" / v1_xgb / "model.json").exists()

    print("\n--- DONE ---")
    
if __name__ == "__main__":
    main()
