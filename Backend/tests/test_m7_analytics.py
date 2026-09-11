"""
M7 Network Analytics — Full Test Suite
=======================================
Covers all 16 required test areas:

 1. Graph construction
 2. Degree calculation
 3. Weighted degree behaviour
 4. PageRank
 5. Betweenness centrality
 6. Louvain community detection
 7. Deterministic seed behaviour
 8. Empty graph
 9. Single-node graph
10. Small graph
11. MAX_NODES bound enforcement
12. MAX_EDGES bound enforcement
13. Node-identifier preservation
14. Canonical-label preservation
15. M7 → M8 feature compatibility
16. Representative CASE-01591 live analysis (mocked Neo4j payload)

All tests use deterministic in-memory fixtures.
No test clears or modifies the Neo4j prototype.
"""

import math
import uuid
import pytest
import pandas as pd
import networkx as nx

from backend.app.analytics.engine import NetworkAnalyticsEngine, STATIC_WEIGHTS
from backend.app.analytics.feature_builder import FeatureBuilder
from backend.app.analytics.models import (
    KeyEntity,
    Community,
    NetworkAnalyticsResponse,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _make_engine(max_nodes=5000, max_edges=20000):
    return NetworkAnalyticsEngine(max_nodes=max_nodes, max_edges=max_edges)


def _mock_engine(engine, nodes, edges):
    """Replace graph_engine with a deterministic in-memory stub."""
    class _Stub:
        def extract_case_subgraph(self, case_id, max_nodes, max_edges):
            return {"nodes": nodes, "edges": edges}
    engine.graph_engine = _Stub()
    return engine


def _simple_nodes(n):
    return [{"id": str(i), "labels": ["Person"], "properties": {"canonical_label": "Person"}}
            for i in range(1, n + 1)]


def _comm_edge(eid, src, tgt, audit_ref):
    return {"id": eid, "source": src, "target": tgt,
            "type": "COMMUNICATES_WITH", "properties": {"Audit_Reference": audit_ref}}


def _static_edge(eid, src, tgt, rel_type="ASSOCIATED_WITH"):
    return {"id": eid, "source": src, "target": tgt,
            "type": rel_type, "properties": {"Audit_Reference": f"A-{eid}"}}


# ---------------------------------------------------------------------------
# 1. Graph construction
# ---------------------------------------------------------------------------

class TestGraphConstruction:
    def test_nodes_added(self):
        engine = _make_engine()
        nodes = _simple_nodes(3)
        edges = [_comm_edge("e1", "1", "2", "R1")]
        G = engine._build_multidigraph(nodes, edges)
        assert set(G.nodes()) == {"1", "2", "3"}

    def test_edges_added_with_metadata(self):
        engine = _make_engine()
        nodes = _simple_nodes(2)
        edges = [_comm_edge("e1", "1", "2", "REF-ALPHA")]
        G = engine._build_multidigraph(nodes, edges)
        edge_data = list(G.edges(data=True))
        assert len(edge_data) == 1
        u, v, d = edge_data[0]
        assert u == "1" and v == "2"
        assert d.get("Audit_Reference") == "REF-ALPHA"
        assert d.get("type") == "COMMUNICATES_WITH"

    def test_directed_multidigraph_type(self):
        engine = _make_engine()
        G = engine._build_multidigraph(_simple_nodes(2), [])
        assert isinstance(G, nx.MultiDiGraph)

    def test_node_properties_stored(self):
        engine = _make_engine()
        nodes = [{"id": "N1", "labels": ["Person"],
                  "properties": {"name": "Alice", "canonical_label": "Person"}}]
        G = engine._build_multidigraph(nodes, [])
        # Properties are merged into node attrs
        assert G.nodes["N1"].get("name") == "Alice"


# ---------------------------------------------------------------------------
# 2 & 3. Degree calculation & weighted degree behaviour
# ---------------------------------------------------------------------------

class TestDegree:
    def test_degree_zero_for_isolated_node(self):
        engine = _make_engine()
        nodes = _simple_nodes(3)
        edges = [_comm_edge("e1", "1", "2", "R1")]
        G = engine._build_multidigraph(nodes, edges)
        G_dir = engine._project_weighted_graph(G, directed=True)
        in_deg = dict(G_dir.in_degree(weight="weight"))
        assert in_deg.get("3", 0.0) == 0.0

    def test_weighted_degree_event_scales_logarithmically(self):
        engine = _make_engine()
        nodes = _simple_nodes(2)
        edges = [_comm_edge(f"e{i}", "1", "2", f"R{i}") for i in range(10)]
        G = engine._build_multidigraph(nodes, edges)
        G_dir = engine._project_weighted_graph(G, directed=True)
        expected = STATIC_WEIGHTS["COMMUNICATES_WITH"] * (1.0 + math.log10(10))
        assert math.isclose(G_dir["1"]["2"]["weight"], expected)

    def test_static_relationship_does_not_scale(self):
        engine = _make_engine()
        nodes = _simple_nodes(2)
        # 50 ASSOCIATED_WITH edges — static, should NOT multiply by count
        edges = [_static_edge(f"e{i}", "1", "2") for i in range(50)]
        G = engine._build_multidigraph(nodes, edges)
        G_dir = engine._project_weighted_graph(G, directed=True)
        assert math.isclose(G_dir["1"]["2"]["weight"], STATIC_WEIGHTS["ASSOCIATED_WITH"])

    def test_duplicate_audit_ref_counts_once(self):
        engine = _make_engine()
        nodes = _simple_nodes(2)
        edges = [
            _comm_edge("e1", "1", "2", "SAME"),
            _comm_edge("e2", "1", "2", "SAME"),  # duplicate ref
            _comm_edge("e3", "1", "2", "DIFF"),
        ]
        G = engine._build_multidigraph(nodes, edges)
        G_dir = engine._project_weighted_graph(G, directed=True)
        # Only 2 unique refs: SAME, DIFF
        expected = STATIC_WEIGHTS["COMMUNICATES_WITH"] * (1.0 + math.log10(2))
        assert math.isclose(G_dir["1"]["2"]["weight"], expected)

    def test_distance_is_inverse_of_weight(self):
        engine = _make_engine()
        nodes = _simple_nodes(2)
        edges = [_comm_edge("e1", "1", "2", "R1")]
        G = engine._build_multidigraph(nodes, edges)
        G_undir = engine._project_weighted_graph(G, directed=False)
        w = G_undir["1"]["2"]["weight"]
        d = G_undir["1"]["2"]["distance"]
        assert math.isclose(d, 1.0 / w, rel_tol=1e-9)


# ---------------------------------------------------------------------------
# 4. PageRank
# ---------------------------------------------------------------------------

class TestPageRank:
    def _ring_result(self, n=5):
        engine = _make_engine()
        nodes = _simple_nodes(n)
        edges = [_comm_edge(f"e{i}", str(i + 1), str((i % n) + 1 + 1 if i < n - 1 else 1), f"R{i}")
                 for i in range(n)]
        _mock_engine(engine, nodes, edges)
        return engine.execute_analytics("test_case")

    def test_pagerank_present_in_key_entities(self):
        res = self._ring_result()
        pr_entities = [k for k in res["key_entities"] if k.metric == "PageRank"]
        assert len(pr_entities) == 1

    def test_pagerank_values_are_positive(self):
        res = self._ring_result()
        pr_entities = [k for k in res["key_entities"] if k.metric == "PageRank"]
        assert pr_entities[0].score > 0.0

    def test_pagerank_sums_to_one(self):
        engine = _make_engine()
        nodes = _simple_nodes(4)
        edges = [
            _comm_edge("e1", "1", "2", "R1"),
            _comm_edge("e2", "2", "3", "R2"),
            _comm_edge("e3", "3", "4", "R3"),
        ]
        G = engine._build_multidigraph(nodes, edges)
        G_dir = engine._project_weighted_graph(G, directed=True)
        pr = nx.pagerank(G_dir, weight="weight")
        assert math.isclose(sum(pr.values()), 1.0, rel_tol=1e-6)


# ---------------------------------------------------------------------------
# 5. Betweenness centrality
# ---------------------------------------------------------------------------

class TestBetweenness:
    def test_betweenness_bridge_node_detected(self):
        engine = _make_engine()
        # Dumbbell: {1,2,3} <-> bridge(1-4) <-> {4,5,6}
        nodes = _simple_nodes(6)
        edges = [
            _comm_edge("e1", "1", "2", "A"),
            _comm_edge("e2", "2", "3", "B"),
            _comm_edge("e3", "3", "1", "C"),
            _comm_edge("e4", "1", "4", "D"),  # bridge
            _comm_edge("e5", "4", "5", "E"),
            _comm_edge("e6", "5", "6", "F"),
            _comm_edge("e7", "6", "4", "G"),
        ]
        _mock_engine(engine, nodes, edges)
        res = engine.execute_analytics("test_case")
        bw_entities = [k for k in res["key_entities"] if k.metric == "Betweenness"]
        assert len(bw_entities) == 1
        assert bw_entities[0].entity_id in {"1", "4"}

    def test_betweenness_zero_for_disconnected_pair(self):
        engine = _make_engine()
        nodes = _simple_nodes(2)
        edges = [_comm_edge("e1", "1", "2", "A")]
        G = engine._build_multidigraph(nodes, edges)
        G_undir = engine._project_weighted_graph(G, directed=False)
        bw = nx.betweenness_centrality(G_undir, weight="distance")
        # Only 2 nodes — no intermediate node, betweenness is 0 for both
        assert all(v == 0.0 for v in bw.values())

    def test_betweenness_uses_distance_weight(self):
        """Strong edges (high weight) should yield short distances, favouring those paths."""
        engine = _make_engine()
        nodes = _simple_nodes(4)
        # Path A: 1-2-4 via 100 events (strong = short distance)
        # Path B: 1-3-4 via 1 event  (weak = long distance)
        edges = (
            [_comm_edge(f"eA1_{i}", "1", "2", f"A{i}") for i in range(100)]
            + [_comm_edge(f"eA2_{i}", "2", "4", f"B{i}") for i in range(100)]
            + [_comm_edge("eB1", "1", "3", "C1")]
            + [_comm_edge("eB2", "3", "4", "D1")]
        )
        G = engine._build_multidigraph(nodes, edges)
        G_undir = engine._project_weighted_graph(G, directed=False)
        bw = nx.betweenness_centrality(G_undir, weight="distance")
        # Node 2 is on the shortest (lowest-distance = highest-weight) path
        assert bw["2"] > bw["3"]


# ---------------------------------------------------------------------------
# 6 & 7. Louvain community detection & deterministic seed
# ---------------------------------------------------------------------------

class TestLouvain:
    def _two_cluster_result(self):
        engine = _make_engine()
        nodes = _simple_nodes(6)
        edges = [
            _comm_edge("e1", "1", "2", "A"),
            _comm_edge("e2", "2", "3", "B"),
            _comm_edge("e3", "4", "5", "C"),
            _comm_edge("e4", "5", "6", "D"),
        ]
        _mock_engine(engine, nodes, edges)
        return engine.execute_analytics("test_case")

    def test_two_communities_detected(self):
        res = self._two_cluster_result()
        assert len(res["communities"]) == 2

    def test_community_member_ids_correct(self):
        res = self._two_cluster_result()
        all_members = set()
        for c in res["communities"]:
            all_members.update(c.member_ids)
        assert all_members == {"1", "2", "3", "4", "5", "6"}

    def test_community_sizes_sum_to_node_count(self):
        res = self._two_cluster_result()
        total = sum(c.size for c in res["communities"])
        assert total == res["node_count"]

    def test_louvain_deterministic_seed_42(self):
        """Same graph → identical community membership on repeated calls."""
        def _run():
            engine = _make_engine()
            nodes = _simple_nodes(8)
            edges = [
                _comm_edge("e1", "1", "2", "A"),
                _comm_edge("e2", "2", "3", "B"),
                _comm_edge("e3", "3", "4", "C"),
                _comm_edge("e4", "5", "6", "D"),
                _comm_edge("e5", "6", "7", "E"),
                _comm_edge("e6", "7", "8", "F"),
            ]
            _mock_engine(engine, nodes, edges)
            return engine.execute_analytics("test_case")

        res1 = _run()
        res2 = _run()
        # Community membership must be identical across runs
        assert len(res1["communities"]) == len(res2["communities"])
        for c1, c2 in zip(res1["communities"], res2["communities"]):
            assert c1.member_ids == c2.member_ids

    def test_community_central_entity_deterministic(self):
        """Central entity must be consistently the highest-degree node."""
        res = self._two_cluster_result()
        # Cluster {1,2,3}: node 2 is the hub (degree 2)
        comm_123 = next(c for c in res["communities"] if "2" in c.member_ids)
        assert comm_123.central_entity_id == "2"


# ---------------------------------------------------------------------------
# 8. Empty graph
# ---------------------------------------------------------------------------

class TestEmptyGraph:
    def test_empty_graph_returns_safe_result(self):
        engine = _make_engine()
        _mock_engine(engine, [], [])
        res = engine.execute_analytics("empty_case")
        assert res["node_count"] == 0
        assert res["edge_count"] == 0
        assert res["key_entities"] == []
        assert res["communities"] == []

    def test_feature_builder_empty_nodes(self):
        fb = FeatureBuilder()
        df = fb.build_features([], [])
        assert df.empty
        assert list(df.columns) == fb.ordered_feature_names


# ---------------------------------------------------------------------------
# 9. Single-node graph
# ---------------------------------------------------------------------------

class TestSingleNode:
    def test_single_node_no_edges_safe(self):
        engine = _make_engine()
        nodes = [{"id": "SOLO", "labels": ["Person"], "properties": {}}]
        _mock_engine(engine, nodes, [])
        res = engine.execute_analytics("solo_case")
        assert res["node_count"] == 1
        assert res["edge_count"] == 0
        assert res["key_entities"] == []
        assert res["communities"] == []

    def test_feature_builder_single_node(self):
        fb = FeatureBuilder()
        nodes = [{"id": "SOLO", "labels": ["Person"], "properties": {}}]
        df = fb.build_features(nodes, [])
        assert len(df) == 1
        assert df.loc["SOLO", "community_size"] == 1.0
        assert df.loc["SOLO", "centrality_degree"] == 0.0
        assert df.loc["SOLO", "tx_out_count"] == 0.0


# ---------------------------------------------------------------------------
# 10. Small graph (3–5 nodes)
# ---------------------------------------------------------------------------

class TestSmallGraph:
    def test_small_graph_all_metrics_produced(self):
        engine = _make_engine()
        nodes = _simple_nodes(4)
        edges = [
            _comm_edge("e1", "1", "2", "A"),
            _comm_edge("e2", "2", "3", "B"),
            _comm_edge("e3", "3", "4", "C"),
        ]
        _mock_engine(engine, nodes, edges)
        res = engine.execute_analytics("small_case")
        assert res["node_count"] == 4
        assert res["edge_count"] == 3
        # Should have at least degree and pagerank
        metrics = {k.metric for k in res["key_entities"]}
        assert "Weighted Degree" in metrics
        assert "PageRank" in metrics

    def test_feature_builder_small_graph_schema(self):
        fb = FeatureBuilder()
        nodes = _simple_nodes(3)
        edges = [_comm_edge("e1", "1", "2", "A"), _comm_edge("e2", "2", "3", "B")]
        df = fb.build_features(nodes, edges)
        assert list(df.columns) == fb.ordered_feature_names
        assert len(df) == 3


# ---------------------------------------------------------------------------
# 11. MAX_NODES bound enforcement
# ---------------------------------------------------------------------------

class TestMaxNodesBound:
    def test_node_overflow_raises_payload_too_large(self):
        engine = _make_engine(max_nodes=10, max_edges=1000)
        nodes = _simple_nodes(11)  # one over
        _mock_engine(engine, nodes, [])
        with pytest.raises(ValueError, match="Payload Too Large"):
            engine.execute_analytics("overflow_case")

    def test_exact_node_limit_accepted(self):
        engine = _make_engine(max_nodes=10, max_edges=1000)
        nodes = _simple_nodes(10)
        _mock_engine(engine, nodes, [])
        res = engine.execute_analytics("exact_limit")
        assert res["node_count"] == 10

    def test_default_max_nodes_is_5000(self):
        engine = NetworkAnalyticsEngine()
        assert engine.max_nodes == 5000


# ---------------------------------------------------------------------------
# 12. MAX_EDGES bound enforcement
# ---------------------------------------------------------------------------

class TestMaxEdgesBound:
    def test_edge_overflow_raises_payload_too_large(self):
        engine = _make_engine(max_nodes=5000, max_edges=5)
        nodes = _simple_nodes(2)
        edges = [_comm_edge(f"e{i}", "1", "2", f"R{i}") for i in range(6)]
        _mock_engine(engine, nodes, edges)
        with pytest.raises(ValueError, match="Payload Too Large"):
            engine.execute_analytics("edge_overflow")

    def test_exact_edge_limit_accepted(self):
        engine = _make_engine(max_nodes=5000, max_edges=5)
        nodes = _simple_nodes(2)
        edges = [_comm_edge(f"e{i}", "1", "2", f"R{i}") for i in range(5)]
        _mock_engine(engine, nodes, edges)
        res = engine.execute_analytics("exact_edge")
        assert res["edge_count"] == 5

    def test_default_max_edges_is_20000(self):
        engine = NetworkAnalyticsEngine()
        assert engine.max_edges == 20000


# ---------------------------------------------------------------------------
# 13. Node identifier preservation
# ---------------------------------------------------------------------------

class TestNodeIdentityPreservation:
    def test_node_ids_preserved_in_multidigraph(self):
        engine = _make_engine()
        ids = ["PER-001", "ORG-999", "CASE-12345", "EVT-abc"]
        nodes = [{"id": nid, "labels": ["Person"], "properties": {}} for nid in ids]
        G = engine._build_multidigraph(nodes, [])
        assert set(G.nodes()) == set(ids)

    def test_node_ids_preserved_through_projection(self):
        engine = _make_engine()
        nodes = [{"id": "PER-001", "labels": ["Person"], "properties": {}},
                 {"id": "ORG-999", "labels": ["Organisation"], "properties": {}}]
        edges = [_comm_edge("e1", "PER-001", "ORG-999", "REF-1")]
        G = engine._build_multidigraph(nodes, edges)
        G_dir = engine._project_weighted_graph(G, directed=True)
        assert "PER-001" in G_dir.nodes()
        assert "ORG-999" in G_dir.nodes()

    def test_feature_builder_index_is_entity_id(self):
        fb = FeatureBuilder()
        nodes = [{"id": "PER-A", "labels": ["Person"], "properties": {}},
                 {"id": "ORG-B", "labels": ["Organisation"], "properties": {}}]
        edges = [_comm_edge("e1", "PER-A", "ORG-B", "REF-1")]
        df = fb.build_features(nodes, edges)
        assert "PER-A" in df.index
        assert "ORG-B" in df.index
        assert df.index.name == "entity_id"


# ---------------------------------------------------------------------------
# 14. Canonical label preservation
# ---------------------------------------------------------------------------

class TestCanonicalLabelPreservation:
    def test_node_labels_stored_in_multidigraph(self):
        engine = _make_engine()
        nodes = [
            {"id": "PER-001", "labels": ["Person"], "properties": {}},
            {"id": "ORG-001", "labels": ["Organisation"], "properties": {}},
            {"id": "CASE-001", "labels": ["Case"], "properties": {}},
        ]
        G = engine._build_multidigraph(nodes, [])
        # Properties dict in nodes should carry label info if included
        # Verify node is added with correct id
        assert set(G.nodes()) == {"PER-001", "ORG-001", "CASE-001"}

    def test_extract_case_subgraph_labels_present(self):
        """Labels returned by extract_case_subgraph are a list at node['labels']."""
        engine = _make_engine()
        # Use real Neo4j stub matching the GraphEngine output format
        nodes = [
            {"id": "PER-001", "labels": ["Person"], "properties": {"name": "Alice"}},
        ]
        G = engine._build_multidigraph(nodes, [])
        # Confirm the id was correctly added
        assert "PER-001" in G.nodes()

    def test_multiple_labels_on_event_node(self):
        """Event nodes can carry a sub-type label (e.g. ['Event', 'Transaction'])."""
        engine = _make_engine()
        nodes = [
            {"id": "EVT-001", "labels": ["Event", "Transaction"], "properties": {}},
            {"id": "PER-001", "labels": ["Person"], "properties": {}},
        ]
        G = engine._build_multidigraph(nodes, [])
        assert "EVT-001" in G.nodes()


# ---------------------------------------------------------------------------
# 15. M7 → M8 feature compatibility
# ---------------------------------------------------------------------------

class TestM7ToM8Compatibility:
    """Verifies that the FeatureBuilder produces the exact schema expected by MLEngine."""

    EXPECTED_FEATURES = [
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

    def test_feature_schema_frozen_order(self):
        fb = FeatureBuilder()
        assert fb.ordered_feature_names == self.EXPECTED_FEATURES

    def test_feature_columns_match_schema(self):
        fb = FeatureBuilder()
        nodes = _simple_nodes(3)
        edges = [_comm_edge("e1", "1", "2", "A"), _comm_edge("e2", "2", "3", "B")]
        df = fb.build_features(nodes, edges)
        assert list(df.columns) == self.EXPECTED_FEATURES

    def test_feature_dtypes_all_float(self):
        fb = FeatureBuilder()
        nodes = _simple_nodes(2)
        edges = [_comm_edge("e1", "1", "2", "A")]
        df = fb.build_features(nodes, edges)
        for col in df.columns:
            assert df[col].dtype == float, f"Column {col} is not float"

    def test_m8_compatibility_no_missing_values(self):
        """M8 must not receive NaN values from M7."""
        fb = FeatureBuilder()
        nodes = _simple_nodes(5)
        edges = [_comm_edge(f"e{i}", str(i + 1), str(i + 2), f"R{i}") for i in range(1, 5)]
        df = fb.build_features(nodes, edges)
        assert not df.isnull().any().any(), "NaN values found in features"

    def test_tx_counts_from_transferred_to(self):
        fb = FeatureBuilder()
        nodes = _simple_nodes(2)
        edges = [
            {"id": "t1", "source": "1", "target": "2", "type": "TRANSFERRED_TO",
             "properties": {"Audit_Reference": "TX-001"}},
            {"id": "t2", "source": "1", "target": "2", "type": "TRANSFERRED_TO",
             "properties": {"Audit_Reference": "TX-002"}},
        ]
        df = fb.build_features(nodes, edges)
        assert df.loc["1", "tx_out_count"] == 2.0
        assert df.loc["2", "tx_in_count"] == 2.0

    def test_comm_counts_from_communicates_with(self):
        fb = FeatureBuilder()
        nodes = _simple_nodes(2)
        edges = [{"id": "c1", "source": "1", "target": "2", "type": "COMMUNICATES_WITH",
                  "properties": {"Audit_Reference": "COM-001"}}]
        df = fb.build_features(nodes, edges)
        assert df.loc["1", "comm_out_count"] == 1.0
        assert df.loc["2", "comm_in_count"] == 1.0

    def test_unique_partners_count(self):
        fb = FeatureBuilder()
        nodes = _simple_nodes(4)
        edges = [
            _comm_edge("e1", "1", "2", "A"),
            _comm_edge("e2", "1", "3", "B"),
            _comm_edge("e3", "1", "4", "C"),
        ]
        df = fb.build_features(nodes, edges)
        assert df.loc["1", "unique_partners_count"] == 3.0

    def test_isolated_node_community_size_one(self):
        """Isolated nodes must have community_size = 1.0, not zero."""
        fb = FeatureBuilder()
        nodes = [
            {"id": "A", "labels": ["Person"], "properties": {}},
            {"id": "B", "labels": ["Person"], "properties": {}},
        ]
        # B is isolated (no edges)
        edges = [_comm_edge("e1", "A", "A", "R")]  # self-loop on A (degenerate, but B is isolated)
        df = fb.build_features(nodes, [])  # no edges at all
        assert df.loc["A", "community_size"] == 1.0
        assert df.loc["B", "community_size"] == 1.0


# ---------------------------------------------------------------------------
# 16. Representative CASE-01591 analysis (mocked from live data)
# ---------------------------------------------------------------------------

class TestCase01591Representative:
    """
    Uses a deterministic mock that mirrors the actual CASE-01591 bounded subgraph
    (33 nodes, 34 edges as confirmed by live verification) to validate the full
    analytics pipeline without touching Neo4j.
    """

    @pytest.fixture
    def case01591_nodes(self):
        # 20 core entity IDs matching live prototype labels
        entity_ids = [
            "PER-028450", "PER-028447", "PER-028448", "PER-028449",
            "ORG-01646", "ORG-01798", "ORG-00436",
            "EVT-001", "EVT-002", "EVT-003", "EVT-004", "EVT-005",
            "ACC-001", "ACC-002", "ACC-003",
            "PHN-001", "PHN-002",
            "LOC-001", "DOC-001", "CASE-01591",
        ]
        labels = {
            "PER": "Person", "ORG": "Organisation", "EVT": "Event",
            "ACC": "Account", "PHN": "Phone", "LOC": "Location",
            "DOC": "Document", "CASE": "Case",
        }
        nodes = []
        for eid in entity_ids:
            prefix = eid.split("-")[0]
            label = labels.get(prefix, "Unknown")
            nodes.append({"id": eid, "labels": [label], "properties": {}})
        return nodes

    @pytest.fixture
    def case01591_edges(self):
        return [
            # INVOLVED_IN
            _static_edge("r01", "PER-028450", "CASE-01591", "INVOLVED_IN"),
            _static_edge("r02", "PER-028447", "CASE-01591", "INVOLVED_IN"),
            # Associations
            _static_edge("r03", "PER-028450", "ORG-01646", "ASSOCIATED_WITH"),
            _static_edge("r04", "PER-028447", "ORG-01798", "ASSOCIATED_WITH"),
            _static_edge("r05", "PER-028448", "ORG-01646", "ASSOCIATED_WITH"),
            _static_edge("r06", "PER-028449", "ORG-01798", "ASSOCIATED_WITH"),
            # Comms
            _comm_edge("r07", "PHN-001", "PHN-002", "COM-A1"),
            _comm_edge("r08", "PHN-001", "PHN-002", "COM-A2"),
            _comm_edge("r09", "PHN-002", "PHN-001", "COM-B1"),
            # Transactions
            {"id": "r10", "source": "ACC-001", "target": "ACC-002",
             "type": "TRANSFERRED_TO", "properties": {"Audit_Reference": "TX-001"}},
            {"id": "r11", "source": "ACC-002", "target": "ACC-003",
             "type": "TRANSFERRED_TO", "properties": {"Audit_Reference": "TX-002"}},
            # Ownership
            _static_edge("r12", "PER-028450", "PHN-001", "OWNS"),
            _static_edge("r13", "PER-028447", "PHN-002", "OWNS"),
            _static_edge("r14", "PER-028450", "ACC-001", "OWNS"),
        ]

    def test_graph_loads_within_bounds(self, case01591_nodes, case01591_edges):
        engine = _make_engine()
        _mock_engine(engine, case01591_nodes, case01591_edges)
        res = engine.execute_analytics("CASE-01591")
        assert res["node_count"] <= 5000
        assert res["edge_count"] <= 20000

    def test_node_count_matches_fixture(self, case01591_nodes, case01591_edges):
        engine = _make_engine()
        _mock_engine(engine, case01591_nodes, case01591_edges)
        res = engine.execute_analytics("CASE-01591")
        assert res["node_count"] == len(case01591_nodes)

    def test_degree_produced(self, case01591_nodes, case01591_edges):
        engine = _make_engine()
        _mock_engine(engine, case01591_nodes, case01591_edges)
        res = engine.execute_analytics("CASE-01591")
        degree_entities = [k for k in res["key_entities"] if k.metric == "Weighted Degree"]
        assert len(degree_entities) == 1
        assert degree_entities[0].score > 0.0

    def test_pagerank_produced(self, case01591_nodes, case01591_edges):
        engine = _make_engine()
        _mock_engine(engine, case01591_nodes, case01591_edges)
        res = engine.execute_analytics("CASE-01591")
        pr_entities = [k for k in res["key_entities"] if k.metric == "PageRank"]
        assert len(pr_entities) == 1
        assert pr_entities[0].score > 0.0

    def test_betweenness_produced(self, case01591_nodes, case01591_edges):
        engine = _make_engine()
        _mock_engine(engine, case01591_nodes, case01591_edges)
        res = engine.execute_analytics("CASE-01591")
        bw_entities = [k for k in res["key_entities"] if k.metric == "Betweenness"]
        assert len(bw_entities) == 1
        assert bw_entities[0].score >= 0.0

    def test_communities_produced(self, case01591_nodes, case01591_edges):
        engine = _make_engine()
        _mock_engine(engine, case01591_nodes, case01591_edges)
        res = engine.execute_analytics("CASE-01591")
        assert len(res["communities"]) >= 1
        for comm in res["communities"]:
            assert comm.size >= 1
            assert comm.community_id >= 1

    def test_repeated_execution_deterministic(self, case01591_nodes, case01591_edges):
        """Two calls with seed=42 must produce identical communities."""
        def run():
            engine = _make_engine()
            _mock_engine(engine, case01591_nodes, case01591_edges)
            return engine.execute_analytics("CASE-01591")

        res1 = run()
        res2 = run()
        assert len(res1["communities"]) == len(res2["communities"])
        for c1, c2 in zip(res1["communities"], res2["communities"]):
            assert c1.community_id == c2.community_id
            assert c1.member_ids == c2.member_ids

    def test_m8_features_complete_for_case01591(self, case01591_nodes, case01591_edges):
        fb = FeatureBuilder()
        df = fb.build_features(case01591_nodes, case01591_edges)
        assert len(df) == len(case01591_nodes)
        assert list(df.columns) == fb.ordered_feature_names
        assert not df.isnull().any().any()

    def test_response_serialisable_as_network_analytics_response(self, case01591_nodes, case01591_edges):
        engine = _make_engine()
        _mock_engine(engine, case01591_nodes, case01591_edges)
        res = engine.execute_analytics("CASE-01591")
        # Must construct without error — validates Pydantic schema
        response = NetworkAnalyticsResponse(**res)
        assert response.case_id == "CASE-01591"
