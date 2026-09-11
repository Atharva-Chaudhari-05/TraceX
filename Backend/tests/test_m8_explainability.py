import pytest
import numpy as np
from unittest.mock import MagicMock
from backend.app.analytics.ml_engine import MLEngine
from m8_test_utils import _train_real_engine, _make_nodes, _make_edges, ORDERED_FEATURES

class TestExplainableFindings:
    def _infer_with_real_models(self, tmp_path, n_nodes=5):
        engine, _, reg = _train_real_engine(tmp_path, n_samples=30, n_pos=15)
        engine.graph_engine = MagicMock()
        engine.graph_engine.extract_case_subgraph.return_value = {
            "nodes": _make_nodes(n_nodes, "SCN-FIN"),
            "edges": _make_edges(_make_nodes(n_nodes, "SCN-FIN")),
        }
        return engine.infer_case("TEST_CASE")

    def test_signals_have_feature_values(self, tmp_path):
        result = self._infer_with_real_models(tmp_path)
        for sig in result["signals"]:
            assert sig["feature_values"] is not None
            assert set(sig["feature_values"].keys()) == set(ORDERED_FEATURES)

    def test_signals_have_explanation(self, tmp_path):
        result = self._infer_with_real_models(tmp_path)
        for sig in result["signals"]:
            assert sig["explanation"] is not None
            assert len(sig["explanation"]) > 10

    def test_explanation_uses_appropriate_language(self, tmp_path):
        result = self._infer_with_real_models(tmp_path)
        for sig in result["signals"]:
            expl = sig["explanation"]
            assert "investigator" in expl.lower(), "Explanation missing investigator reference"
            assert "synthetic" in expl.lower(), "Explanation missing synthetic disclaimer"
            for forbidden in ["guilty", "confirmed fraud", "is a criminal", "criminal activity", "offender", "confirmed criminal network"]:
                assert forbidden not in expl.lower(), f"Forbidden language found: {forbidden}"

    def test_signals_have_top_features(self, tmp_path):
        result = self._infer_with_real_models(tmp_path)
        for sig in result["signals"]:
            assert sig["top_features"] is not None
            assert isinstance(sig["top_features"], list)
            assert len(sig["top_features"]) <= 3

    def test_top_features_are_valid_feature_names(self, tmp_path):
        result = self._infer_with_real_models(tmp_path)
        for sig in result["signals"]:
            for feat in sig["top_features"]:
                assert feat in ORDERED_FEATURES, f"Unknown feature: {feat}"

    def test_generate_explanation_high_risk_language(self):
        engine = MLEngine()
        expl = engine._generate_explanation(0.85, True, ["centrality_degree"])
        assert "high-risk" in expl.lower() or "High-risk" in expl

    def test_generate_explanation_low_risk_language(self):
        engine = MLEngine()
        expl = engine._generate_explanation(0.1, False, [])
        assert "low" in expl.lower()

    def test_generate_explanation_anomaly_language(self):
        engine = MLEngine()
        expl = engine._generate_explanation(0.5, True, [])
        assert "anomalous" in expl.lower()

    def test_metadata_contains_disclaimer(self, tmp_path):
        result = self._infer_with_real_models(tmp_path)
        disclaimer = result["metadata"].get("synthetic_target_disclaimer", "")
        assert "synthetic" in disclaimer.lower()
        assert "not" in disclaimer.lower()

    def test_anomaly_score_lower_is_more_anomalous(self, tmp_path):
        result = self._infer_with_real_models(tmp_path, n_nodes=10)
        anomalies = [s["anomaly_score"] for s in result["signals"] if s["is_anomaly"]]
        non_anomalies = [s["anomaly_score"] for s in result["signals"] if not s["is_anomaly"]]
        if anomalies and non_anomalies:
            assert np.mean(anomalies) <= np.mean(non_anomalies)
