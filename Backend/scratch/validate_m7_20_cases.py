from backend.app.graph.engine import GraphEngine
from backend.app.analytics.engine import NetworkAnalyticsEngine
from backend.app.analytics.feature_builder import FeatureBuilder

CASES = [
    "CASE-01591", "CASE-00394", "CASE-01744", "CASE-00184",
    "CASE-00529", "CASE-00959", "CASE-01084", "CASE-01664",
    "CASE-00564", "CASE-01209", "CASE-01334", "CASE-01594",
    "CASE-00349", "CASE-01269", "CASE-01994", "CASE-00139",
    "CASE-01519", "CASE-01124", "CASE-01059", "CASE-01584",
]

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

MAX_NODES = 5000
MAX_EDGES = 20000

print("========================================")
print("M7 - 20 CASE ANALYTICS VERIFICATION")
print("========================================")

graph = GraphEngine()
analytics = NetworkAnalyticsEngine()
features = FeatureBuilder()

passed = 0

try:
    for case_id in CASES:

        print(f"\n[{case_id}]")

        # ------------------------------------------
        # Obtain the actual case subgraph
        # ------------------------------------------

        subgraph = graph.extract_case_subgraph(
            case_id,
            max_nodes=MAX_NODES,
            max_edges=MAX_EDGES,
        )

        nodes = subgraph["nodes"]
        edges = subgraph["edges"]

        node_count = len(nodes)
        edge_count = len(edges)

        print(f"  Nodes          : {node_count}")
        print(f"  Edges          : {edge_count}")

        # ------------------------------------------
        # Execute M7 twice
        # ------------------------------------------

        result1 = analytics.execute_analytics(case_id)
        result2 = analytics.execute_analytics(case_id)

        # ------------------------------------------
        # Validate result structure
        # ------------------------------------------

        required_keys = [
            "case_id",
            "node_count",
            "edge_count",
            "key_entities",
            "communities",
        ]

        structure_ok = all(
            key in result1 for key in required_keys
        )

        print(
            f"  Result structure: "
            f"{'PASS' if structure_ok else 'FAIL'}"
        )

        # ------------------------------------------
        # Verify counts agree with graph extraction
        # ------------------------------------------

        counts_ok = (
            result1.get("case_id") == case_id
            and result1.get("node_count") == node_count
            and result1.get("edge_count") == edge_count
        )

        print(
            f"  Count agreement : "
            f"{'PASS' if counts_ok else 'FAIL'}"
        )

        # ------------------------------------------
        # M7 bounds
        # ------------------------------------------

        bounds_ok = (
            node_count <= MAX_NODES
            and edge_count <= MAX_EDGES
        )

        print(
            f"  Bounds          : "
            f"{'PASS' if bounds_ok else 'FAIL'}"
        )

        # ------------------------------------------
        # Key entity analytics
        # ------------------------------------------

        key_entities = result1.get("key_entities", [])

        metrics = set()

        for entity in key_entities:
            if isinstance(entity, dict):
                metrics.add(entity.get("metric"))
            else:
                metric = getattr(entity, "metric", None)
                if metric:
                    metrics.add(metric)

        required_metrics = {
            "Weighted Degree",
            "PageRank",
            "Betweenness",
        }

        metrics_ok = required_metrics.issubset(metrics)

        print(
            f"  Centrality      : "
            f"{'PASS' if metrics_ok else 'CHECK'} "
            f"| metrics={sorted(metrics)}"
        )

        # ------------------------------------------
        # Louvain communities
        # ------------------------------------------

        communities = result1.get("communities", [])

        communities_ok = len(communities) > 0

        print(
            f"  Communities     : "
            f"{'PASS' if communities_ok else 'FAIL'} "
            f"| count={len(communities)}"
        )

        # ------------------------------------------
        # Determinism
        # ------------------------------------------

        deterministic = str(result1) == str(result2)

        print(
            f"  Deterministic    : "
            f"{'PASS' if deterministic else 'FAIL'}"
        )

        # ------------------------------------------
        # M8 feature compatibility
        # ------------------------------------------

        feature_df = features.build_features(nodes, edges)

        columns = list(feature_df.columns)
        missing = [
            column
            for column in EXPECTED_FEATURES
            if column not in columns
        ]

        nan_count = int(feature_df.isna().sum().sum())

        features_ok = (
            not missing
            and nan_count == 0
            and len(feature_df) == node_count
        )

        print(
            f"  M8 features     : "
            f"{'PASS' if features_ok else 'FAIL'} "
            f"| shape={feature_df.shape} "
            f"| NaN={nan_count}"
        )

        if missing:
            print(f"    Missing       : {missing}")

        # ------------------------------------------
        # Final case gate
        # ------------------------------------------

        case_ok = (
            structure_ok
            and counts_ok
            and bounds_ok
            and metrics_ok
            and communities_ok
            and deterministic
            and features_ok
        )

        if case_ok:
            print("  RESULT          : PASS")
            passed += 1
        else:
            print("  RESULT          : CHECK")

finally:
    try:
        graph.driver.close()
    except Exception:
        pass

print("\n========================================")
print(f"M7 20-CASE COVERAGE: {passed}/20")
print("========================================")

if passed == 20:
    print("M7 20-CASE VERIFICATION: PASS")
else:
    print("M7 20-CASE VERIFICATION: CHECK REQUIRED")
