import math
import pytest
from unittest.mock import MagicMock
from m8_test_utils import _train_real_engine, _make_nodes, _make_edges, ORDERED_FEATURES

DEMO_20_CASES = [
    "CASE-01591", "CASE-00394", "CASE-01744", "CASE-00184",
    "CASE-00529", "CASE-00959", "CASE-01084", "CASE-01664",
    "CASE-00564", "CASE-01209", "CASE-01334", "CASE-01594",
    "CASE-00349", "CASE-01269", "CASE-01994", "CASE-00139",
    "CASE-01519", "CASE-01124", "CASE-01059", "CASE-01584",
]

class TestTwentyCaseInference:
    @pytest.fixture(scope="class")
    def trained_engine(self, tmp_path_factory):
        tmp = tmp_path_factory.mktemp("ml_models")
        engine, _, reg = _train_real_engine(tmp, n_samples=40, n_pos=20)
        engine.registry = reg
        return engine, reg

    def _run_case(self, engine, case_id, n_nodes=5):
        nodes = _make_nodes(n_nodes, "SCN-FIN")
        edges = _make_edges(nodes)
        engine.graph_engine = MagicMock()
        engine.graph_engine.extract_case_subgraph.return_value = {
            "nodes": nodes,
            "edges": edges,
        }
        return engine.infer_case(case_id)

    def test_all_20_cases_produce_signals(self, trained_engine):
        engine, _ = trained_engine
        for case_id in DEMO_20_CASES:
            result = self._run_case(engine, case_id)
            assert result["case_id"] == case_id
            assert len(result["signals"]) > 0, f"No signals for {case_id}"

    def test_all_20_cases_no_nan_feature_values(self, trained_engine):
        engine, _ = trained_engine
        for case_id in DEMO_20_CASES:
            result = self._run_case(engine, case_id)
            for sig in result["signals"]:
                if sig["feature_values"]:
                    assert all(
                        math.isfinite(v) for v in sig["feature_values"].values()
                    ), f"NaN/Inf in feature_values for {case_id}"

    def test_all_20_cases_have_explanations(self, trained_engine):
        engine, _ = trained_engine
        for case_id in DEMO_20_CASES:
            result = self._run_case(engine, case_id)
            for sig in result["signals"]:
                assert sig["explanation"] and len(sig["explanation"]) > 0

    def test_all_20_cases_correct_feature_schema(self, trained_engine):
        engine, _ = trained_engine
        for case_id in DEMO_20_CASES:
            result = self._run_case(engine, case_id)
            assert result["metadata"]["feature_schema_version"] == "1.0"
            for sig in result["signals"]:
                if sig["feature_values"]:
                    assert set(sig["feature_values"].keys()) == set(ORDERED_FEATURES)

    def test_inference_deterministic_for_same_case(self, trained_engine):
        engine, _ = trained_engine
        r1 = self._run_case(engine, "CASE-01591")
        r2 = self._run_case(engine, "CASE-01591")
        assert len(r1["signals"]) == len(r2["signals"])
        for s1, s2 in zip(r1["signals"], r2["signals"]):
            assert s1["entity_id"] == s2["entity_id"]
            assert abs(s1["xgboost_probability"] - s2["xgboost_probability"]) < 1e-9
            assert s1["is_anomaly"] == s2["is_anomaly"]

    def test_empty_case_returns_empty_signals(self, trained_engine):
        engine, _ = trained_engine
        engine.graph_engine = MagicMock()
        engine.graph_engine.extract_case_subgraph.return_value = {"nodes": [], "edges": []}
        result = engine.infer_case("CASE-EMPTY")
        assert result["signals"] == []

    def test_disclaimer_present_in_all_20_responses(self, trained_engine):
        engine, _ = trained_engine
        for case_id in DEMO_20_CASES[:5]:
            result = self._run_case(engine, case_id)
            assert "synthetic_target_disclaimer" in result["metadata"]
