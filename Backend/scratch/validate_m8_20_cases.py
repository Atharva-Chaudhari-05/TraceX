import numpy as np

from backend.app.analytics.engine import NetworkAnalyticsEngine
from backend.app.analytics.feature_builder import FeatureBuilder
from backend.app.analytics.ml_engine import MLEngine

CASES = [
    "CASE-01591",
    "CASE-00394",
    "CASE-01744",
    "CASE-00184",
    "CASE-00529",
    "CASE-00959",
    "CASE-01084",
    "CASE-01664",
    "CASE-00564",
    "CASE-01209",
    "CASE-01334",
    "CASE-01594",
    "CASE-00349",
    "CASE-01269",
    "CASE-01994",
    "CASE-00139",
    "CASE-01519",
    "CASE-01124",
    "CASE-01059",
    "CASE-01584",
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

print("=" * 80)
print("M8 MANUAL 20-CASE VALIDATION")
print("=" * 80)

analytics = NetworkAnalyticsEngine()
feature_builder = FeatureBuilder()
ml_engine = MLEngine()

passed = 0

for case_id in CASES:
    try:
        subgraph = analytics.graph_engine.extract_case_subgraph(
            case_id,
            max_nodes=5000,
            max_edges=20000,
        )

        nodes = subgraph["nodes"]
        edges = subgraph["edges"]

        # Feature pipeline
        df = feature_builder.build_features(nodes, edges)

        assert len(df) == len(nodes), (
            f"feature row count {len(df)} != node count {len(nodes)}"
        )

        assert list(df.columns) == EXPECTED_FEATURES, (
            f"feature schema mismatch: {list(df.columns)}"
        )

        assert not df.isna().any().any(), "NaN detected"

        values = df.to_numpy(dtype=float)

        assert np.isfinite(values).all(), (
            "Infinity or non-finite feature value detected"
        )

        # Real inference
        result = ml_engine.infer_case(case_id)

        assert result is not None, "infer_case returned None"

        print(
            f"[PASS] {case_id:<12} "
            f"nodes={len(nodes):<4} "
            f"edges={len(edges):<4} "
            f"features={df.shape}"
        )

        passed += 1

    except Exception as exc:
        print(
            f"[FAIL] {case_id:<12} "
            f"{type(exc).__name__}: {exc}"
        )

print("=" * 80)
print(f"M8 20-CASE COVERAGE: {passed}/{len(CASES)}")

if passed == len(CASES):
    print("M8 20-CASE VERIFICATION: PASS")
else:
    print("M8 20-CASE VERIFICATION: FAIL")

print("=" * 80)