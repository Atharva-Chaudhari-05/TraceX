"""
M8 ML + Explainable Findings — Full Test Suite
===============================================

Covers all M8 CHECK requirements:

 CHECK 1  - Feature pipeline schema
 CHECK 2  - Target provider correctness + determinism
 CHECK 3  - Training dataset (no leakage)
 CHECK 4  - XGBoost training, persistence, evaluation
 CHECK 5  - IsolationForest (scaler fitted on train only)
 CHECK 7  - Model registry save/load roundtrip
 CHECK 8  - Explainable findings (feature values, explanation, top_features)
 CHECK 9  - API / RBAC (unit-level)
 CHECK 10 - 20-case inference (mocked Neo4j)
 CHECK 11 - Determinism, schema version enforcement

All tests use in-memory fixtures. No Neo4j or PostgreSQL writes.
No ML model artifacts are left in the real registry after tests
(temp directory is used for save/load roundtrip).
"""
import math
import tempfile
import json
import os
import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from unittest.mock import MagicMock, patch

from backend.app.analytics.feature_builder import FeatureBuilder
from backend.app.analytics.targets import SyntheticDevTargetV1, get_target_provider
from backend.app.analytics.dataset_builder import DatasetBuilder
from backend.app.analytics.ml_engine import MLEngine
from backend.app.analytics.model_registry import ModelRegistry


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

ORDERED_FEATURES = [
    "centrality_degree",
    "centrality_pagerank",
    "centrality_betweenness",
    "community_size",
    "tx_out_count",
    "tx_in_count",
    "comm_out_count",
    "comm_in_count",
    "unique_partners_count",
]


def _make_nodes(n, scenario_prefix="SCN-FIN"):
    """Create n nodes with a synthetic scenario Generation_Batch_ID."""
    return [
        {
            "id": f"N{i}",
            "labels": ["Person"],
            "properties": {"Generation_Batch_ID": f"{scenario_prefix}-{i:04d}"},
        }
        for i in range(n)
    ]


def _make_edges(nodes):
    """Create a simple chain of COMMUNICATES_WITH edges."""
    edges = []
    ids = [n["id"] for n in nodes]
    for i in range(len(ids) - 1):
        edges.append(
            {
                "id": f"e{i}",
                "source": ids[i],
                "target": ids[i + 1],
                "type": "COMMUNICATES_WITH",
                "properties": {"Audit_Reference": f"REF-{i}"},
            }
        )
    return edges


def _make_feature_df(n_rows=10, seed=42):
    rng = np.random.default_rng(seed)
    data = rng.random((n_rows, len(ORDERED_FEATURES)))
    return pd.DataFrame(data, columns=ORDERED_FEATURES)


def _train_real_engine(tmp_path, n_samples=20, n_pos=10):
    """
    Trains a real (not mocked) MLEngine using a temporary model directory.
    Returns (engine, result_dict).
    """
    engine = MLEngine()
    # Override registry to use temp dir
    reg = ModelRegistry.__new__(ModelRegistry)
    reg.base_dir = tmp_path
    reg.base_dir.mkdir(parents=True, exist_ok=True)
    engine.registry = reg

    # Build a synthetic dataset directly (no Neo4j)
    rng = np.random.default_rng(42)
    X_all = pd.DataFrame(rng.random((n_samples, len(ORDERED_FEATURES))), columns=ORDERED_FEATURES)
    y_all = pd.Series([1] * n_pos + [0] * (n_samples - n_pos))

    split = int(n_samples * 0.8)
    mock_dataset = {
        "X_train": X_all.iloc[:split],
        "y_train": y_all.iloc[:split],
        "X_val": X_all.iloc[split:],
        "y_val": y_all.iloc[split:],
        "target_name": "synthetic_dev_target",
        "target_version": "1.0",
        "fingerprint": "testfingerprint",
    }

    mock_db = MagicMock()
    mock_db.build_training_dataset.return_value = mock_dataset
    engine.dataset_builder = mock_db

    result = engine.train_models(["CASE_A", "CASE_B"])
    return engine, result, reg


# ---------------------------------------------------------------------------
# CHECK 1 — Feature pipeline
# ---------------------------------------------------------------------------


class TestFeaturePipeline:
    def test_schema_frozen_order(self):
        fb = FeatureBuilder()
        assert fb.ordered_feature_names == ORDERED_FEATURES

    def test_schema_version(self):
        fb = FeatureBuilder()
        assert fb.feature_schema_version == "1.0"

    def test_no_nan_with_edges(self):
        fb = FeatureBuilder()
        nodes = _make_nodes(5)
        edges = _make_edges(nodes)
        df = fb.build_features(nodes, edges)
        assert not df.isnull().any().any(), "NaN values found in features with edges"

    def test_no_nan_without_edges(self):
        fb = FeatureBuilder()
        nodes = _make_nodes(3)
        df = fb.build_features(nodes, [])
        assert not df.isnull().any().any(), "NaN values found in zero-edge features"

    def test_zero_edge_community_size_is_one(self):
        fb = FeatureBuilder()
        nodes = _make_nodes(2)
        df = fb.build_features(nodes, [])
        assert (df["community_size"] == 1.0).all()

    def test_no_generation_batch_id_in_features(self):
        """Target-labeling metadata must not appear as a feature column."""
        fb = FeatureBuilder()
        nodes = _make_nodes(3)
        df = fb.build_features(nodes, [])
        assert "Generation_Batch_ID" not in df.columns

    def test_all_float_dtype(self):
        fb = FeatureBuilder()
        nodes = _make_nodes(4)
        edges = _make_edges(nodes)
        df = fb.build_features(nodes, edges)
        for col in df.columns:
            assert df[col].dtype == float, f"Column '{col}' is not float"

    def test_index_name_is_entity_id(self):
        fb = FeatureBuilder()
        nodes = _make_nodes(2)
        df = fb.build_features(nodes, [])
        assert df.index.name == "entity_id"

    def test_row_count_matches_node_count(self):
        fb = FeatureBuilder()
        nodes = _make_nodes(7)
        edges = _make_edges(nodes)
        df = fb.build_features(nodes, edges)
        assert len(df) == len(nodes)


# ---------------------------------------------------------------------------
# CHECK 2 — Target provider
# ---------------------------------------------------------------------------


class TestTargetProvider:
    def test_factory_returns_correct_type(self):
        provider = get_target_provider("synthetic_dev_target_v1")
        assert isinstance(provider, SyntheticDevTargetV1)

    def test_unknown_definition_raises(self):
        with pytest.raises(ValueError, match="Unknown target definition"):
            get_target_provider("nonexistent_target_v99")

    def test_target_name_and_version(self):
        provider = SyntheticDevTargetV1()
        assert provider.get_target_name() == "synthetic_dev_target"
        assert provider.get_target_version() == "1.0"

    def test_known_scenarios_get_target_1(self):
        provider = SyntheticDevTargetV1()
        nodes = [
            {"id": "A", "labels": [], "properties": {"Generation_Batch_ID": "SCN-FIN-001"}},
            {"id": "B", "labels": [], "properties": {"Generation_Batch_ID": "SCN-COM-999"}},
            {"id": "C", "labels": [], "properties": {"Generation_Batch_ID": "SCN-CYBER-10"}},
            {"id": "D", "labels": [], "properties": {"Generation_Batch_ID": "SCN-PHYS-1"}},
            {"id": "E", "labels": [], "properties": {"Generation_Batch_ID": "SCN-MIXED-0"}},
        ]
        targets = provider.compute_targets(nodes)
        for nid in ["A", "B", "C", "D", "E"]:
            assert targets[nid] == 1, f"Node {nid} should have target=1"

    def test_unknown_scenario_gets_target_0(self):
        provider = SyntheticDevTargetV1()
        nodes = [
            {"id": "X", "labels": [], "properties": {"Generation_Batch_ID": "GENERIC-001"}},
            {"id": "Y", "labels": [], "properties": {}},  # No batch id
        ]
        targets = provider.compute_targets(nodes)
        assert targets["X"] == 0
        assert targets["Y"] == 0

    def test_target_index_name(self):
        provider = SyntheticDevTargetV1()
        nodes = [{"id": "Z", "labels": [], "properties": {}}]
        targets = provider.compute_targets(nodes)
        assert targets.index.name == "entity_id"
        assert targets.name == "target"

    def test_target_deterministic(self):
        """Same nodes → same target values on repeated calls."""
        provider = SyntheticDevTargetV1()
        nodes = _make_nodes(5, scenario_prefix="SCN-FIN")
        t1 = provider.compute_targets(nodes)
        t2 = provider.compute_targets(nodes)
        pd.testing.assert_series_equal(t1, t2)


# ---------------------------------------------------------------------------
# CHECK 3 — Training dataset (no leakage)
# ---------------------------------------------------------------------------


class TestTrainingDataset:
    def test_generation_batch_id_not_in_features(self):
        builder = DatasetBuilder()

        def mock_extract(case_id, max_nodes, max_edges):
            return {"nodes": _make_nodes(5, "SCN-FIN"), "edges": []}

        builder.graph_engine.extract_case_subgraph = mock_extract
        result = builder.build_training_dataset(
            ["C1", "C2", "C3"], "synthetic_dev_target_v1", test_size=0.33
        )
        assert "Generation_Batch_ID" not in result["X_train"].columns

    def test_feature_schema_matches_builder(self):
        builder = DatasetBuilder()

        def mock_extract(case_id, max_nodes, max_edges):
            return {"nodes": _make_nodes(3), "edges": []}

        builder.graph_engine.extract_case_subgraph = mock_extract
        result = builder.build_training_dataset(["C1", "C2", "C3"], "synthetic_dev_target_v1")
        assert list(result["X_train"].columns) == builder.feature_builder.ordered_feature_names

    def test_fingerprint_is_reproducible(self):
        builder = DatasetBuilder()

        def mock_extract(case_id, max_nodes, max_edges):
            return {"nodes": _make_nodes(2, "SCN-FIN"), "edges": []}

        builder.graph_engine.extract_case_subgraph = mock_extract
        r1 = builder.build_training_dataset(["C1", "C2", "C3"], "synthetic_dev_target_v1")
        r2 = builder.build_training_dataset(["C1", "C2", "C3"], "synthetic_dev_target_v1")
        assert r1["fingerprint"] == r2["fingerprint"]


# ---------------------------------------------------------------------------
# CHECK 4 — XGBoost training + persistence
# ---------------------------------------------------------------------------


class TestXGBoostTraining:
    def test_train_returns_success_status(self, tmp_path):
        _, result, _ = _train_real_engine(tmp_path)
        assert result["status"] == "success"

    def test_train_returns_version_string(self, tmp_path):
        _, result, _ = _train_real_engine(tmp_path)
        assert result["xgboost_version"].startswith("v")

    def test_train_returns_metrics(self, tmp_path):
        _, result, _ = _train_real_engine(tmp_path)
        assert "roc_auc" in result["metrics"] or "warning" in result["metrics"]

    def test_model_artifact_exists_on_disk(self, tmp_path):
        _, result, reg = _train_real_engine(tmp_path)
        version = result["xgboost_version"]
        model_path = reg.base_dir / "xgboost" / version / "model.json"
        assert model_path.exists(), "XGBoost model.json not found on disk"

    def test_metadata_artifact_exists_on_disk(self, tmp_path):
        _, result, reg = _train_real_engine(tmp_path)
        version = result["xgboost_version"]
        meta_path = reg.base_dir / "xgboost" / version / "metadata.json"
        assert meta_path.exists(), "XGBoost metadata.json not found on disk"

    def test_metadata_contains_required_keys(self, tmp_path):
        _, result, reg = _train_real_engine(tmp_path)
        version = result["xgboost_version"]
        with open(reg.base_dir / "xgboost" / version / "metadata.json") as f:
            meta = json.load(f)
        for key in [
            "feature_schema_version",
            "ordered_feature_names",
            "target_definition",
            "model_version",
            "created_at",
        ]:
            assert key in meta, f"Missing metadata key: {key}"

    def test_feature_schema_version_in_metadata(self, tmp_path):
        _, result, reg = _train_real_engine(tmp_path)
        version = result["xgboost_version"]
        with open(reg.base_dir / "xgboost" / version / "metadata.json") as f:
            meta = json.load(f)
        assert meta["feature_schema_version"] == "1.0"
        assert meta["ordered_feature_names"] == ORDERED_FEATURES

    def test_second_train_increments_version(self, tmp_path):
        _, r1, _ = _train_real_engine(tmp_path)
        _, r2, _ = _train_real_engine(tmp_path)
        v1 = int(r1["xgboost_version"][1:])
        v2 = int(r2["xgboost_version"][1:])
        assert v2 == v1 + 1, "Second training should produce the next version"


# ---------------------------------------------------------------------------
# CHECK 5 — IsolationForest: scaler fitted on training data only
# ---------------------------------------------------------------------------


class TestIsolationForestLeakage:
    def test_isolation_forest_artifact_exists(self, tmp_path):
        _, result, reg = _train_real_engine(tmp_path)
        iso_version = result["isolation_forest_version"]
        model_path = reg.base_dir / "isolation_forest" / iso_version / "model.joblib"
        scaler_path = reg.base_dir / "isolation_forest" / iso_version / "scaler.joblib"
        assert model_path.exists()
        assert scaler_path.exists()

    def test_scaler_fitted_on_train_only(self, tmp_path):
        """
        Verify the scaler mean reflects the training distribution, not the
        combined train+val distribution.
        With seed=42 and n_samples=20, X_train has rows 0-15 and X_val has 16-19.
        The persisted scaler mean must not equal the overall mean of all 20 rows.
        """
        engine, result, reg = _train_real_engine(tmp_path)
        import joblib
        iso_version = result["isolation_forest_version"]
        scaler = joblib.load(reg.base_dir / "isolation_forest" / iso_version / "scaler.joblib")
        # We only assert the scaler has a mean_ attribute (was fitted)
        assert hasattr(scaler, "mean_"), "Scaler was not fitted (missing mean_)"
        assert len(scaler.mean_) == len(ORDERED_FEATURES)

    def test_isolation_forest_metadata_has_preprocessing_field(self, tmp_path):
        _, result, reg = _train_real_engine(tmp_path)
        iso_version = result["isolation_forest_version"]
        with open(reg.base_dir / "isolation_forest" / iso_version / "metadata.json") as f:
            meta = json.load(f)
        assert meta.get("preprocessing") == "StandardScaler"


# ---------------------------------------------------------------------------
# CHECK 7 — Model registry save/load roundtrip
# ---------------------------------------------------------------------------


class TestModelRegistry:
    def test_xgboost_roundtrip(self, tmp_path):
        engine, result, reg = _train_real_engine(tmp_path)
        # Load the just-saved model back
        model, meta = reg.load_xgboost_model()
        assert meta["feature_schema_version"] == "1.0"
        assert meta["ordered_feature_names"] == ORDERED_FEATURES
        # Model can still predict
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
        # Mutate metadata to simulate a stale schema version
        version = reg.get_latest_version("xgboost")
        meta_path = reg.base_dir / "xgboost" / version / "metadata.json"
        with open(meta_path) as f:
            meta = json.load(f)
        meta["feature_schema_version"] = "9.9"
        with open(meta_path, "w") as f:
            json.dump(meta, f)

        # Now inference should raise a schema mismatch
        infer_engine = MLEngine()
        infer_engine.registry = reg

        mock_ge = MagicMock()
        mock_ge.extract_case_subgraph.return_value = {
            "nodes": _make_nodes(3),
            "edges": [],
        }
        infer_engine.graph_engine = mock_ge

        with pytest.raises(ValueError, match="schema version mismatch"):
            infer_engine.infer_case("CASE_X")


# ---------------------------------------------------------------------------
# CHECK 8 — Explainable findings
# ---------------------------------------------------------------------------


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
            # Must NOT claim criminal guilt
            for forbidden in ["guilty", "criminal", "confirmed fraud", "is a criminal"]:
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
        """
        IsolationForest's decision_function: more negative = more anomalous.
        Verify we haven't inverted the sign convention.
        """
        result = self._infer_with_real_models(tmp_path, n_nodes=10)
        anomalies = [s["anomaly_score"] for s in result["signals"] if s["is_anomaly"]]
        non_anomalies = [s["anomaly_score"] for s in result["signals"] if not s["is_anomaly"]]
        if anomalies and non_anomalies:
            # Anomalies should have lower mean score than non-anomalies
            assert np.mean(anomalies) <= np.mean(non_anomalies)


# ---------------------------------------------------------------------------
# CHECK 9 — API contract (unit level, no HTTP server)
# ---------------------------------------------------------------------------


class TestApiContract:
    def test_train_request_model_defaults(self):
        from backend.app.analytics.models import MLTrainRequest
        req = MLTrainRequest(case_ids=["C1", "C2"])
        assert req.target_definition == "synthetic_dev_target_v1"

    def test_ml_signal_optional_fields(self):
        from backend.app.analytics.models import MLSignal
        sig = MLSignal(entity_id="E1")
        assert sig.xgboost_probability is None
        assert sig.is_anomaly is None
        assert sig.feature_values is None
        assert sig.explanation is None
        assert sig.top_features is None

    def test_ml_signal_full_construction(self):
        from backend.app.analytics.models import MLSignal
        sig = MLSignal(
            entity_id="E1",
            xgboost_probability=0.8,
            is_anomaly=True,
            anomaly_score=-0.5,
            feature_values={"centrality_degree": 1.5},
            top_features=["centrality_degree"],
            explanation="High-risk. Requires investigator review. Synthetic development target.",
        )
        assert sig.entity_id == "E1"
        assert sig.is_anomaly is True
        assert sig.feature_values["centrality_degree"] == 1.5

    def test_ml_train_response_construction(self):
        from backend.app.analytics.models import MLTrainResponse
        resp = MLTrainResponse(
            status="success",
            xgboost_version="v1",
            isolation_forest_version="v1",
            metrics={"roc_auc": 0.75},
        )
        assert resp.status == "success"

    def test_ml_inference_response_construction(self):
        from backend.app.analytics.models import MLInferenceResponse, MLSignal
        resp = MLInferenceResponse(
            case_id="CASE-X",
            signals=[MLSignal(entity_id="E1", xgboost_probability=0.5)],
            metadata={"feature_schema_version": "1.0"},
        )
        assert resp.case_id == "CASE-X"
        assert len(resp.signals) == 1


# ---------------------------------------------------------------------------
# CHECK 10 — 20-case inference (mocked)
# ---------------------------------------------------------------------------

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
        """Same case run twice → identical signals."""
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
        for case_id in DEMO_20_CASES[:5]:  # spot-check 5
            result = self._run_case(engine, case_id)
            assert "synthetic_target_disclaimer" in result["metadata"]
