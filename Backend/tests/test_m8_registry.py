import json
import pytest
from unittest.mock import MagicMock
from backend.app.analytics.ml_engine import MLEngine
from backend.app.analytics.model_registry import ModelRegistry
from m8_test_utils import _train_real_engine, _make_feature_df, _make_nodes, ORDERED_FEATURES

class TestModelRegistry:
    def test_xgboost_roundtrip(self, tmp_path):
        engine, result, reg = _train_real_engine(tmp_path)
        model, meta = reg.load_xgboost_model()
        assert meta["feature_schema_version"] == "1.0"
        assert meta["ordered_feature_names"] == ORDERED_FEATURES
        X = _make_feature_df(3)
        probs = model.predict_proba(X)
        assert probs.shape == (3, 2)

    def test_isolation_forest_roundtrip(self, tmp_path):
        engine, result, reg = _train_real_engine(tmp_path)
        model, scaler, meta = reg.load_isolation_forest_model()
        assert meta["feature_schema_version"] == "1.0"
        X = _make_feature_df(3)
        X_scaled = scaler.transform(X)
        preds = model.predict(X_scaled)
        assert set(preds).issubset({1, -1})

    def test_load_without_models_raises(self, tmp_path):
        reg = ModelRegistry.__new__(ModelRegistry)
        reg.base_dir = tmp_path
        with pytest.raises(ValueError, match="No models found"):
            reg.load_xgboost_model()

    def test_get_next_version_starts_at_v1(self, tmp_path):
        reg = ModelRegistry.__new__(ModelRegistry)
        reg.base_dir = tmp_path
        assert reg.get_next_version("xgboost") == "v1"

    def test_schema_version_mismatch_raises(self, tmp_path):
        engine, _, reg = _train_real_engine(tmp_path)
        version = reg.get_latest_version("xgboost")
        meta_path = reg.base_dir / "xgboost" / version / "metadata.json"
        with open(meta_path) as f:
            meta = json.load(f)
        meta["feature_schema_version"] = "9.9"
        with open(meta_path, "w") as f:
            json.dump(meta, f)

        infer_engine = MLEngine()
        infer_engine.registry = reg
        mock_ge = MagicMock()
        mock_ge.extract_case_subgraph.return_value = {"nodes": _make_nodes(3), "edges": []}
        infer_engine.graph_engine = mock_ge

        with pytest.raises(ValueError, match="schema version mismatch"):
            infer_engine.infer_case("CASE_X")
