import os
from backend.app.graph.engine import GraphEngine
from backend.app.analytics.engine import NetworkAnalyticsEngine
from backend.app.analytics.feature_builder import FeatureBuilder

g = GraphEngine()
engine = NetworkAnalyticsEngine()
engine.graph_engine = g
fb = FeatureBuilder()

sub = g.extract_case_subgraph("CASE-01591")
nodes, edges = sub["nodes"], sub["edges"]

print("=== LIVE CASE-01591 PROTOTYPE VALIDATION ===")
print(f"Nodes loaded: {len(nodes)} (bounds: <=5000)")
print(f"Edges loaded: {len(edges)} (bounds: <=20000)")
assert len(nodes) <= 5000, "NODE BOUND EXCEEDED"
assert len(edges) <= 20000, "EDGE BOUND EXCEEDED"

# Full analytics
res = engine.execute_analytics("CASE-01591")
print()
print(f"Analytics node_count: {res['node_count']}")
print(f"Analytics edge_count: {res['edge_count']}")
print()
print("Key Entities:")
for ke in res["key_entities"]:
    print(f"  [{ke.metric}] {ke.entity_id} score={ke.score:.6f}")
print()
print(f"Communities: {len(res['communities'])}")
for c in res["communities"]:
    print(f"  community_id={c.community_id} size={c.size} central={c.central_entity_id}")

# Determinism check
res2 = engine.execute_analytics("CASE-01591")
assert len(res["communities"]) == len(res2["communities"]), "NON-DETERMINISTIC"
for c1, c2 in zip(res["communities"], res2["communities"]):
    assert c1.member_ids == c2.member_ids, f"NON-DETERMINISTIC members for comm {c1.community_id}"
print()
print("Determinism: PASS (seed=42, 2 identical runs)")

# M8 feature build
df = fb.build_features(nodes, edges)
assert list(df.columns) == fb.ordered_feature_names, "FEATURE SCHEMA MISMATCH"
assert not df.isnull().any().any(), "NaN VALUES IN FEATURES"
print()
print("M8 Feature Matrix:")
print(f"  shape: {df.shape}")
print(f"  columns: {list(df.columns)}")
print(f"  non-zero degree: {(df['centrality_degree']>0).sum()}")
print(f"  non-zero pagerank: {(df['centrality_pagerank']>0).sum()}")
print(f"  NaN count: {df.isnull().sum().sum()}")
print()
print("=== M7 -> M8 COMPATIBILITY: PASS ===")
