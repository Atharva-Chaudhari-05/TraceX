import pytest
import networkx as nx
import math
from backend.app.analytics.engine import NetworkAnalyticsEngine

def test_sentinel_overflow_nodes():
    # If Neo4j returns exactly 5001 nodes, it should raise ValueError
    engine = NetworkAnalyticsEngine(max_nodes=5000, max_edges=20000)
    
    # We can mock extract_case_subgraph
    class MockGraphEngine:
        def extract_case_subgraph(self, case_id, max_nodes, max_edges):
            return {
                "nodes": [{"id": str(i)} for i in range(5001)],
                "edges": []
            }
            
    engine.graph_engine = MockGraphEngine()
    
    with pytest.raises(ValueError, match="Payload Too Large"):
        engine.execute_analytics("test_case")

def test_sentinel_overflow_edges():
    # If Neo4j returns exactly 20001 edges, it should raise ValueError
    engine = NetworkAnalyticsEngine(max_nodes=5000, max_edges=20000)
    
    class MockGraphEngine:
        def extract_case_subgraph(self, case_id, max_nodes, max_edges):
            return {
                "nodes": [{"id": "1"}, {"id": "2"}],
                "edges": [{"id": str(i), "source": "1", "target": "2", "type": "COMMUNICATES_WITH", "properties": {}} for i in range(20001)]
            }
            
    engine.graph_engine = MockGraphEngine()
    
    with pytest.raises(ValueError, match="Payload Too Large"):
        engine.execute_analytics("test_case")

def test_exact_limit_acceptance():
    engine = NetworkAnalyticsEngine(max_nodes=50, max_edges=200) # smaller limits for test
    
    class MockGraphEngine:
        def extract_case_subgraph(self, case_id, max_nodes, max_edges):
            return {
                "nodes": [{"id": str(i)} for i in range(50)],
                "edges": [{"id": str(i), "source": "1", "target": "2", "type": "COMMUNICATES_WITH", "properties": {}} for i in range(200)]
            }
            
    engine.graph_engine = MockGraphEngine()
    
    # Should not raise exception
    res = engine.execute_analytics("test_case")
    assert res["node_count"] == 50
    assert res["edge_count"] == 200

def test_duplicate_event_deduplication():
    # If multiple edges have same Audit_Reference, they count as 1 event
    engine = NetworkAnalyticsEngine()
    
    nodes = [{"id": "1"}, {"id": "2"}]
    edges = [
        {"id": "e1", "source": "1", "target": "2", "type": "COMMUNICATES_WITH", "properties": {"Audit_Reference": "A"}},
        {"id": "e2", "source": "1", "target": "2", "type": "COMMUNICATES_WITH", "properties": {"Audit_Reference": "A"}}, # Duplicate ref
        {"id": "e3", "source": "1", "target": "2", "type": "COMMUNICATES_WITH", "properties": {"Audit_Reference": "B"}}
    ]
    
    G_multi = engine._build_multidigraph(nodes, edges)
    G_proj = engine._project_weighted_graph(G_multi, directed=True)
    
    # Total unique refs = 2
    # Weight = 0.2 * (1 + log10(2)) = 0.2 * 1.301 = 0.2602
    expected_weight = 0.2 * (1.0 + math.log10(2))
    assert math.isclose(G_proj["1"]["2"]["weight"], expected_weight)

def test_logarithmic_weighting_logic():
    engine = NetworkAnalyticsEngine()
    
    nodes = [{"id": "1"}, {"id": "2"}]
    edges = [{"id": f"e{i}", "source": "1", "target": "2", "type": "COMMUNICATES_WITH", "properties": {"Audit_Reference": f"A{i}"}} for i in range(100)]
    
    G_multi = engine._build_multidigraph(nodes, edges)
    G_proj = engine._project_weighted_graph(G_multi, directed=True)
    
    # Total unique refs = 100
    # Weight = 0.2 * (1 + log10(100)) = 0.2 * (1 + 2) = 0.6
    assert math.isclose(G_proj["1"]["2"]["weight"], 0.6)

def test_static_relationship_weighting():
    engine = NetworkAnalyticsEngine()
    
    nodes = [{"id": "1"}, {"id": "2"}]
    # 5 USES relationships. Since USES is static, its structural weight is fixed (1.0).
    # It does not scale, preventing duplicate rows from inflating the weight.
    edges = [{"id": f"e{i}", "source": "1", "target": "2", "type": "USES", "properties": {"Audit_Reference": f"A{i}"}} for i in range(5)]
    
    G_multi = engine._build_multidigraph(nodes, edges)
    G_proj = engine._project_weighted_graph(G_multi, directed=True)
    
    # Weight = 1.0
    assert math.isclose(G_proj["1"]["2"]["weight"], 1.0)

def test_betweenness_and_pagerank():
    engine = NetworkAnalyticsEngine()
    
    # Dumbbell graph: Cluster 1 (1,2,3) connected to Cluster 2 (4,5,6) via bridge (1 -> 4)
    nodes = [{"id": str(i)} for i in range(1, 7)]
    edges = [
        # Cluster 1
        {"id": "e1", "source": "1", "target": "2", "type": "COMMUNICATES_WITH", "properties": {"Audit_Reference": "A"}},
        {"id": "e2", "source": "2", "target": "3", "type": "COMMUNICATES_WITH", "properties": {"Audit_Reference": "B"}},
        {"id": "e3", "source": "3", "target": "1", "type": "COMMUNICATES_WITH", "properties": {"Audit_Reference": "C"}},
        
        # Bridge
        {"id": "e4", "source": "1", "target": "4", "type": "COMMUNICATES_WITH", "properties": {"Audit_Reference": "D"}},
        
        # Cluster 2
        {"id": "e5", "source": "4", "target": "5", "type": "COMMUNICATES_WITH", "properties": {"Audit_Reference": "E"}},
        {"id": "e6", "source": "5", "target": "6", "type": "COMMUNICATES_WITH", "properties": {"Audit_Reference": "F"}},
        {"id": "e7", "source": "6", "target": "4", "type": "COMMUNICATES_WITH", "properties": {"Audit_Reference": "G"}},
    ]
    
    class MockGraphEngine:
        def extract_case_subgraph(self, case_id, max_nodes, max_edges):
            return {"nodes": nodes, "edges": edges}
            
    engine.graph_engine = MockGraphEngine()
    
    res = engine.execute_analytics("test_case")
    
    # Node 1 and 4 should be critical bridges (Betweenness)
    bridge_entities = [k for k in res["key_entities"] if k.metric == "Betweenness"]
    assert bridge_entities[0].entity_id in ["1", "4"]

def test_betweenness_weight_as_distance():
    # Test where strength vs distance matters for Betweenness
    engine = NetworkAnalyticsEngine()
    
    # We create two clusters connected by TWO paths:
    # Path A: nodes 1-2-3 (strong edges, should be shortest distance)
    # Path B: nodes 1-4-3 (weak edges, should be longer distance)
    nodes = [{"id": str(i)} for i in range(1, 5)]
    edges = [
        # Path A: Very strong (many duplicated events = high weight)
        *([{"id": f"eA1_{i}", "source": "1", "target": "2", "type": "COMMUNICATES_WITH", "properties": {"Audit_Reference": f"A{i}"}} for i in range(100)]),
        *([{"id": f"eA2_{i}", "source": "2", "target": "3", "type": "COMMUNICATES_WITH", "properties": {"Audit_Reference": f"B{i}"}} for i in range(100)]),
        # Path B: Very weak (only 1 event)
        {"id": "eB1", "source": "1", "target": "4", "type": "COMMUNICATES_WITH", "properties": {"Audit_Reference": "C1"}},
        {"id": "eB2", "source": "4", "target": "3", "type": "COMMUNICATES_WITH", "properties": {"Audit_Reference": "D1"}}
    ]
    
    class MockGraphEngine:
        def extract_case_subgraph(self, case_id, max_nodes, max_edges):
            return {"nodes": nodes, "edges": edges}
            
    engine.graph_engine = MockGraphEngine()
    res = engine.execute_analytics("test_case")
    
    # Since weight is correctly transformed to distance = 1/weight, 
    # Path A has much shorter distance (e.g. 1/0.6 vs 1/0.2)
    # Betweenness routing will prefer 1-2-3. Therefore, node 2 should be the primary bridge, not node 4.
    bridge_entities = [k for k in res["key_entities"] if k.metric == "Betweenness"]
    assert len(bridge_entities) > 0
    # Node 2 is the bridge because it lies on the shortest path (strongest connection)
    assert bridge_entities[0].entity_id == "2"

def test_louvain_modularity_behavior():
    engine = NetworkAnalyticsEngine()
    
    # Two distinctly disconnected components to force two clear communities
    nodes = [{"id": str(i)} for i in range(1, 7)]
    edges = [
        {"id": "e1", "source": "1", "target": "2", "type": "COMMUNICATES_WITH", "properties": {"Audit_Reference": "A"}},
        {"id": "e2", "source": "2", "target": "3", "type": "COMMUNICATES_WITH", "properties": {"Audit_Reference": "B"}},
        {"id": "e3", "source": "4", "target": "5", "type": "COMMUNICATES_WITH", "properties": {"Audit_Reference": "C"}},
        {"id": "e4", "source": "5", "target": "6", "type": "COMMUNICATES_WITH", "properties": {"Audit_Reference": "D"}}
    ]
    
    class MockGraphEngine:
        def extract_case_subgraph(self, case_id, max_nodes, max_edges):
            return {"nodes": nodes, "edges": edges}
            
    engine.graph_engine = MockGraphEngine()
    res = engine.execute_analytics("test_case")
    
    communities = res["communities"]
    assert len(communities) == 2
    # Verify deterministic sorting (size desc, then central ID asc)
    # Both are size 3. Members are (1,2,3) and (4,5,6).
    # Comm 1 should have member 1,2,3
    assert set(communities[0].member_ids) == {"1", "2", "3"}
    assert set(communities[1].member_ids) == {"4", "5", "6"}
    
    # Check that central entity is deterministically chosen
    # For Comm 1, Node 2 has degree 2 (highest), Nodes 1,3 have degree 1
    assert communities[0].central_entity_id == "2"
    assert communities[1].central_entity_id == "5"

def test_zero_edge_case_extraction():
    engine = NetworkAnalyticsEngine()
    
    # Test how the engine handles a case where Neo4j extraction yields nodes but 0 edges
    class MockGraphEngine:
        def extract_case_subgraph(self, case_id, max_nodes, max_edges):
            return {"nodes": [{"id": "1"}, {"id": "2"}], "edges": []}
            
    engine.graph_engine = MockGraphEngine()
    res = engine.execute_analytics("test_empty")
    
    assert res["node_count"] == 2
    assert res["edge_count"] == 0
    assert len(res["key_entities"]) == 0
    assert len(res["communities"]) == 0