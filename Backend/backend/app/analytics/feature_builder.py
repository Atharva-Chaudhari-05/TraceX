import logging
from typing import Dict, List, Any
import pandas as pd
import networkx as nx
from networkx.algorithms.community import louvain_communities

from backend.app.analytics.engine import NetworkAnalyticsEngine

logger = logging.getLogger(__name__)

class FeatureBuilder:
    def __init__(self):
        self.network_engine = NetworkAnalyticsEngine()
        self.feature_schema_version = "1.0"
        self.ordered_feature_names = [
            "centrality_degree",
            "centrality_pagerank",
            "centrality_betweenness",
            "community_size",
            "tx_out_count",
            "tx_in_count",
            "comm_out_count",
            "comm_in_count",
            "unique_partners_count"
        ]

    def build_features(self, nodes: List[Dict], edges: List[Dict]) -> pd.DataFrame:
        """
        Builds the deterministic M8 feature schema v1.0 for all nodes in the given case subgraph.
        Returns a pandas DataFrame where index is entity_id.
        """
        node_ids = [n["id"] for n in nodes]
        if not node_ids:
            return pd.DataFrame(columns=self.ordered_feature_names)

        if not edges:
            # Zero edges - all structural and event counts are legitimately zero
            df = pd.DataFrame(0.0, index=node_ids, columns=self.ordered_feature_names)
            df.index.name = "entity_id"
            # Isolated nodes are technically a community of 1
            df["community_size"] = 1.0
            return df

        G_multi = self.network_engine._build_multidigraph(nodes, edges)
        G_dir = self.network_engine._project_weighted_graph(G_multi, directed=True)
        G_undir = self.network_engine._project_weighted_graph(G_multi, directed=False)

        # 1. centrality_degree (Weighted In-Degree on G_dir)
        in_degree = dict(G_dir.in_degree(weight="weight"))
        
        # 2. centrality_pagerank (PageRank on G_dir)
        try:
            pr = nx.pagerank(G_dir, weight="weight")
        except Exception as e:
            logger.warning(f"PageRank failed to converge, defaulting to 0.0: {e}")
            pr = {n: 0.0 for n in node_ids}
            
        # 3. centrality_betweenness (Betweenness on G_undir using weight="distance")
        try:
            bw = nx.betweenness_centrality(G_undir, weight="distance")
        except Exception as e:
            logger.warning(f"Betweenness failed, defaulting to 0.0: {e}")
            bw = {n: 0.0 for n in node_ids}
            
        # 4. community_size (Louvain on G_undir)
        try:
            louvain_comms = louvain_communities(G_undir, weight="weight", seed=42)
        except Exception as e:
            logger.warning(f"Louvain failed, defaulting to size 1: {e}")
            louvain_comms = [{n} for n in node_ids]

        node_to_comm_size = {}
        for comm in louvain_comms:
            size = len(comm)
            for n in comm:
                node_to_comm_size[n] = size

        # Initialize raw counts
        tx_out = {n: 0 for n in node_ids}
        tx_in = {n: 0 for n in node_ids}
        comm_out = {n: 0 for n in node_ids}
        comm_in = {n: 0 for n in node_ids}
        partners = {n: set() for n in node_ids}

        # Calculate behavioral features from G_multi directly.
        # Use setdefault to handle edge endpoints that reference node IDs not
        # present in the original `nodes` list (dangling references in the graph).
        for u, v, k, data in G_multi.edges(keys=True, data=True):
            rel_type = data.get("type")
            partners.setdefault(u, set()).add(v)
            partners.setdefault(v, set()).add(u)
            if rel_type == "TRANSFERRED_TO":
                tx_out[u] = tx_out.get(u, 0) + 1
                tx_in[v] = tx_in.get(v, 0) + 1
            elif rel_type == "COMMUNICATES_WITH":
                comm_out[u] = comm_out.get(u, 0) + 1
                comm_in[v] = comm_in.get(v, 0) + 1

        feature_rows = []
        for n in node_ids:
            # Genuine zeros if node is isolated or missing from metrics
            feature_rows.append({
                "entity_id": n,
                "centrality_degree": float(in_degree.get(n, 0.0)),
                "centrality_pagerank": float(pr.get(n, 0.0)),
                "centrality_betweenness": float(bw.get(n, 0.0)),
                "community_size": float(node_to_comm_size.get(n, 1.0)), # isolated node is a community of 1
                "tx_out_count": float(tx_out.get(n, 0.0)),
                "tx_in_count": float(tx_in.get(n, 0.0)),
                "comm_out_count": float(comm_out.get(n, 0.0)),
                "comm_in_count": float(comm_in.get(n, 0.0)),
                "unique_partners_count": float(len(partners.get(n, set())))
            })

        df = pd.DataFrame(feature_rows)
        df.set_index("entity_id", inplace=True)
        # Enforce exact frozen order
        return df[self.ordered_feature_names]
