import pytest
import pandas as pd
from unittest.mock import MagicMock
from backend.app.analytics.targets import SyntheticDevTargetV1, get_target_provider
from backend.app.analytics.dataset_builder import DatasetBuilder
from m8_test_utils import _make_nodes

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
            {"id": "Y", "labels": [], "properties": {}},
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
        provider = SyntheticDevTargetV1()
        nodes = _make_nodes(5, scenario_prefix="SCN-FIN")
        t1 = provider.compute_targets(nodes)
        t2 = provider.compute_targets(nodes)
        pd.testing.assert_series_equal(t1, t2)

class TestTrainingDataset:
    def test_generation_batch_id_not_in_features(self):
        builder = DatasetBuilder()
        def mock_extract(case_id, max_nodes, max_edges):
            return {"nodes": _make_nodes(5, "SCN-FIN"), "edges": []}
        builder.graph_engine.extract_case_subgraph = mock_extract
        result = builder.build_training_dataset(["C1", "C2", "C3"], "synthetic_dev_target_v1", test_size=0.33)
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
