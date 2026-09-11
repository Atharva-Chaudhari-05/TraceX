import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch

from backend.app.analytics.feature_builder import FeatureBuilder
from backend.app.analytics.targets import SyntheticDevTargetV1, get_target_provider
from backend.app.analytics.dataset_builder import DatasetBuilder
from backend.app.analytics.ml_engine import MLEngine

# Fixtures for testing

@pytest.fixture
def mock_subgraph():
    nodes = [
        {"id": "E1", "labels": ["Person"], "properties": {"Generation_Batch_ID": "SCN-FIN-0001"}},
        {"id": "E2", "labels": ["Person"], "properties": {"Generation_Batch_ID": "SCN-COM-0002"}},
        {"id": "E3", "labels": ["Organization"], "properties": {"Generation_Batch_ID": "OTHER"}},
        {"id": "E4", "labels": ["Person"], "properties": {}} # Isolated
    ]
    edges = [
        # E1 -> E2 (TRANSFERRED_TO)
        {"id": "r1", "source": "E1", "target": "E2", "type": "TRANSFERRED_TO", "properties": {"Audit_Reference": "A1"}},
        {"id": "r2", "source": "E1", "target": "E2", "type": "TRANSFERRED_TO", "properties": {"Audit_Reference": "A2"}},
        # E2 -> E3 (COMMUNICATES_WITH)
        {"id": "r3", "source": "E2", "target": "E3", "type": "COMMUNICATES_WITH", "properties": {"Audit_Reference": "A3"}}
    ]
    return nodes, edges


def test_feature_builder_schema(mock_subgraph):
    nodes, edges = mock_subgraph
    builder = FeatureBuilder()
    
    df = builder.build_features(nodes, edges)
    
    assert list(df.columns) == builder.ordered_feature_names
    assert len(df) == 4
    
    # Check E1 (2 transfers out)
    assert df.loc["E1", "tx_out_count"] == 2.0
    assert df.loc["E1", "tx_in_count"] == 0.0
    assert df.loc["E1", "comm_out_count"] == 0.0
    
    # Check E2 (2 transfers in, 1 comm out)
    assert df.loc["E2", "tx_in_count"] == 2.0
    assert df.loc["E2", "comm_out_count"] == 1.0
    
    # Check E4 (isolated, genuine zeros)
    assert df.loc["E4", "tx_out_count"] == 0.0
    assert df.loc["E4", "tx_in_count"] == 0.0
    assert df.loc["E4", "centrality_degree"] == 0.0
    assert df.loc["E4", "community_size"] == 1.0

def test_feature_builder_zero_edges():
    builder = FeatureBuilder()
    nodes = [{"id": "E1"}, {"id": "E2"}]
    df = builder.build_features(nodes, [])
    
    assert len(df) == 2
    assert df.loc["E1", "tx_out_count"] == 0.0
    assert df.loc["E1", "community_size"] == 1.0

def test_synthetic_target_provider(mock_subgraph):
    nodes, _ = mock_subgraph
    provider = get_target_provider("synthetic_dev_target_v1")
    
    targets = provider.compute_targets(nodes)
    
    assert targets.name == "target"
    assert targets.index.name == "entity_id"
    
    assert targets["E1"] == 1 # SYNTH_SCENARIO_1 is in known
    assert targets["E2"] == 1 # SYNTH_SCENARIO_2 is in known
    assert targets["E3"] == 0 # OTHER
    assert targets["E4"] == 0 # None

def test_dataset_builder_grouping():
    # Mock GraphEngine
    builder = DatasetBuilder()
    
    nodes_1 = [{"id": "C1_N1", "properties": {"Generation_Batch_ID": "SCN-FIN-0001"}}]
    edges_1 = []
    
    nodes_2 = [{"id": "C2_N1", "properties": {"Generation_Batch_ID": "OTHER"}}]
    edges_2 = []
    
    nodes_3 = [{"id": "C3_N1", "properties": {"Generation_Batch_ID": "SCN-FIN-0002"}}]
    edges_3 = []

    # Monkeypatch extract_case_subgraph
    def mock_extract(case_id, max_nodes, max_edges):
        if case_id == "CASE_1": return {"nodes": nodes_1, "edges": edges_1}
        if case_id == "CASE_2": return {"nodes": nodes_2, "edges": edges_2}
        if case_id == "CASE_3": return {"nodes": nodes_3, "edges": edges_3}
        return {"nodes": [], "edges": []}
        
    builder.graph_engine.extract_case_subgraph = mock_extract
    
    res = builder.build_training_dataset(["CASE_1", "CASE_2", "CASE_3"], "synthetic_dev_target_v1", test_size=0.33, random_seed=42)
    
    # Given 3 cases, group shuffle split should put some in train, some in val
    assert res["X_train"] is not None
    assert res["X_val"] is not None
    assert len(res["X_train"]) > 0
    assert len(res["X_val"]) > 0
    
    # Target leakage check: ensure Generation_Batch_ID isn't in features
    assert "Generation_Batch_ID" not in res["X_train"].columns
    assert list(res["X_train"].columns) == builder.feature_builder.ordered_feature_names

@patch("backend.app.analytics.ml_engine.ModelRegistry")
@patch("backend.app.analytics.ml_engine.DatasetBuilder")
def test_ml_engine_train(MockDatasetBuilder, MockModelRegistry):
    engine = MLEngine()
    
    # Setup mock dataset
    mock_db = MockDatasetBuilder.return_value
    mock_db.build_training_dataset.return_value = {
        "X_train": pd.DataFrame([[0]*9, [1]*9, [2]*9, [3]*9], columns=engine.feature_builder.ordered_feature_names),
        "y_train": pd.Series([0, 1, 0, 1]),
        "X_val": pd.DataFrame([[0]*9, [1]*9], columns=engine.feature_builder.ordered_feature_names),
        "y_val": pd.Series([0, 1]),
        "target_name": "test_target",
        "target_version": "1.0",
        "fingerprint": "hash123"
    }
    engine.dataset_builder = mock_db
    
    mock_reg = MockModelRegistry.return_value
    mock_reg.save_xgboost_model.return_value = "v1"
    mock_reg.save_isolation_forest_model.return_value = "v1"
    engine.registry = mock_reg
    
    result = engine.train_models(["CASE_1", "CASE_2"])
    
    assert result["status"] == "success"
    assert result["xgboost_version"] == "v1"
    assert "roc_auc" in result["metrics"]
    assert mock_reg.save_xgboost_model.called
    assert mock_reg.save_isolation_forest_model.called

@patch("backend.app.analytics.ml_engine.ModelRegistry")
@patch("backend.app.analytics.ml_engine.GraphEngine")
def test_ml_engine_infer(MockGraphEngine, MockModelRegistry):
    engine = MLEngine()
    
    # Mock subgraph
    mock_ge = MockGraphEngine.return_value
    mock_ge.extract_case_subgraph.return_value = {
        "nodes": [{"id": "E1"}],
        "edges": []
    }
    engine.graph_engine = mock_ge
    
    # Mock registry
    mock_reg = MockModelRegistry.return_value
    
    # Create dummy models
    class DummyXGB:
        def __init__(self):
            self.feature_importances_ = [0.1] * 9

        def predict_proba(self, X):
            return np.array([[0.2, 0.8]])
            
    class DummyIso:
        def predict(self, X):
            return [-1]
        def decision_function(self, X):
            return [-0.5]
            
    class DummyScaler:
        def transform(self, X):
            return X
            
    xgb_meta = {
        "model_version": "v1",
        "feature_schema_version": "1.0",
        "ordered_feature_names": engine.feature_builder.ordered_feature_names
    }
    iso_meta = {
        "model_version": "v1",
        "feature_schema_version": "1.0",
        "ordered_feature_names": engine.feature_builder.ordered_feature_names
    }
    
    mock_reg.load_xgboost_model.return_value = (DummyXGB(), xgb_meta)
    mock_reg.load_isolation_forest_model.return_value = (DummyIso(), DummyScaler(), iso_meta)
    engine.registry = mock_reg
    
    res = engine.infer_case("CASE_1")
    
    assert res["case_id"] == "CASE_1"
    assert len(res["signals"]) == 1
    signal = res["signals"][0]
    assert signal["entity_id"] == "E1"
    assert signal["xgboost_probability"] == 0.8
    assert signal["is_anomaly"] is True
    assert signal["anomaly_score"] == -0.5
