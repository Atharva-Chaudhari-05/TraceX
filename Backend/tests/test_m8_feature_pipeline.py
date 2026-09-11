import pytest
import pandas as pd
from backend.app.analytics.feature_builder import FeatureBuilder
from m8_test_utils import ORDERED_FEATURES, _make_nodes, _make_edges

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
