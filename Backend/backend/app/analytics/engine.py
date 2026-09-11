import logging
import math
from typing import Dict, List, Any, Tuple
import networkx as nx
from networkx.algorithms.community import louvain_communities

from backend.app.graph.engine import GraphEngine
from backend.app.analytics.models import KeyEntity, Community, Explanation, InsightType

logger = logging.getLogger(__name__)

STATIC_WEIGHTS = {
    "OWNS": 1.0,
    "WORKS_FOR": 1.0,
    "ASSOCIATED_WITH": 1.0,
    "USES": 1.0,
    "LOCATED_AT": 0.5,
    "CONNECTED_TO": 0.5,
    "PARTICIPATED_IN": 0.5,
    "INVOLVED_IN": 0.5,
    "HAS_DOCUMENT": 0.5,
    "HAS_EVENT": 0.5,
    "TRANSFERRED_TO": 1.0, # treated as event but base weight 1.0
    "COMMUNICATES_WITH": 0.2
}

class NetworkAnalyticsEngine:
    def __init__(self, max_nodes: int = 5000, max_edges: int = 20000):
        self.max_nodes = max_nodes
        self.max_edges = max_edges
        self.graph_engine = GraphEngine()

    def _build_multidigraph(self, nodes_data: List[Dict], edges_data: List[Dict]) -> nx.MultiDiGraph:
        """
        Builds the base provenance MultiDiGraph from Neo4j payload.
        """
        G = nx.MultiDiGraph()
        
        for n in nodes_data:
            G.add_node(n["id"], **n.get("properties", {}))
            
        for e in edges_data:
            props = dict(e["properties"])
            audit_ref = props.pop("Audit_Reference", "UNKNOWN")
            G.add_edge(
                e["source"],
                e["target"],
                key=e["id"],
                type=e["type"],
                Audit_Reference=audit_ref,
                **props
            )
            
        return G

    def _project_weighted_graph(self, G_multi: nx.MultiDiGraph, directed: bool = True) -> nx.Graph:
        """
        Projects the MultiDiGraph to a weighted Graph/DiGraph using logarithmic frequency scaling.
        Event count = Count of unique Audit_References for a relationship type between two nodes.
        Weight = Base_Weight * (1 + log10(Event Count))
        """
        if directed:
            G_proj = nx.DiGraph()
        else:
            G_proj = nx.Graph()
            
        for n in G_multi.nodes():
            G_proj.add_node(n, **G_multi.nodes[n])
            
        # We need to aggregate edges between (u, v)
        # We group by relationship type
        # For undirected, (u,v) and (v,u) are merged. For directed, they are separate.
        
        edge_groups = {}
        for u, v, k, data in G_multi.edges(keys=True, data=True):
            if not directed:
                # canonicalize direction
                u, v = (min(u, v), max(u, v))
                
            rel_type = data.get("type")
            audit_ref = data.get("Audit_Reference")
            
            pair_key = (u, v)
            if pair_key not in edge_groups:
                edge_groups[pair_key] = {}
                
            if rel_type not in edge_groups[pair_key]:
                edge_groups[pair_key][rel_type] = set()
                
            if audit_ref:
                edge_groups[pair_key][rel_type].add(audit_ref)
                
        for (u, v), types_dict in edge_groups.items():
            total_weight = 0.0
            
            for rel_type, audit_refs in types_dict.items():
                count = len(audit_refs) if audit_refs else 1
                base_weight = STATIC_WEIGHTS.get(rel_type, 0.5)
                
                # Check if it's a static relationship (no scaling)
                # We define static as any relationship where base_weight > 0 and not explicitly frequency based
                # For safety, TraceX defined COMMUNICATES_WITH and TRANSFERRED_TO as freq-based, 
                # but TRANSFERRED_TO could be static. The plan says EVENT_RELATIONSHIPS scale.
                # USES is explicitly static.
                if rel_type in ["COMMUNICATES_WITH", "TRANSFERRED_TO"]:
                    weight = base_weight * (1.0 + math.log10(count))
                else:
                    weight = base_weight # Static relationships do not scale by count
                    
                total_weight += weight
                
            if total_weight > 0:
                # If projecting to undirected, we sum weights.
                distance = 1.0 / total_weight
                if G_proj.has_edge(u, v):
                    G_proj[u][v]["weight"] += total_weight
                    G_proj[u][v]["distance"] = 1.0 / G_proj[u][v]["weight"]
                else:
                    G_proj.add_edge(u, v, weight=total_weight, distance=distance)
                    
        return G_proj

    def execute_analytics(self, case_id: str) -> Dict[str, Any]:
        # 1. Extract subgraph
        # Note: We fetch MAX + 1 to detect overflow
        subgraph_data = self.graph_engine.extract_case_subgraph(
            case_id, max_nodes=self.max_nodes, max_edges=self.max_edges
        )
        
        nodes = subgraph_data["nodes"]
        edges = subgraph_data["edges"]
        
        node_count = len(nodes)
        edge_count = len(edges)
        
        # 2. Sentinel checks
        if node_count > self.max_nodes or edge_count > self.max_edges:
            raise ValueError(f"Payload Too Large: Graph exceeds {self.max_nodes} nodes or {self.max_edges} edges.")
            
        if node_count == 0:
            return {
                "case_id": case_id,
                "node_count": 0,
                "edge_count": 0,
                "key_entities": [],
                "communities": []
            }

        # 3. Build base graph
        G_multi = self._build_multidigraph(nodes, edges)
        
        # 4. Build Projections
        G_dir = self._project_weighted_graph(G_multi, directed=True)
        G_undir = self._project_weighted_graph(G_multi, directed=False)
        
        # We need a fallback if there are no edges
        if edge_count == 0:
            return {
                "case_id": case_id,
                "node_count": node_count,
                "edge_count": 0,
                "key_entities": [],
                "communities": []
            }

        key_entities_list = []
        
        # -- Degree Centrality (Directed) --
        # Weighted In-Degree for Activity
        in_degree = dict(G_dir.in_degree(weight="weight"))
        # Sort deterministic: score desc, id asc
        sorted_degree = sorted(in_degree.items(), key=lambda x: (-x[1], x[0]))
        if sorted_degree and sorted_degree[0][1] > 0:
            top_deg_node, top_deg_score = sorted_degree[0]
            key_entities_list.append(
                KeyEntity(
                    entity_id=top_deg_node,
                    metric="Weighted Degree",
                    score=top_deg_score,
                    explanation=Explanation(
                        what="High Activity",
                        why="This entity has a high volume of frequency-scaled direct connections.",
                        supporting_evidence=[],
                        provenance=f"Derived from {node_count} nodes and {edge_count} relationships in the operational graph."
                    )
                )
            )
            
        # -- PageRank (Directed) --
        # Try-except for convergence
        try:
            pr = nx.pagerank(G_dir, weight="weight")
            sorted_pr = sorted(pr.items(), key=lambda x: (-x[1], x[0]))
            if sorted_pr:
                top_pr_node, top_pr_score = sorted_pr[0]
                key_entities_list.append(
                    KeyEntity(
                        entity_id=top_pr_node,
                        metric="PageRank",
                        score=top_pr_score,
                        explanation=Explanation(
                            what="High Structural Influence",
                            why="This entity maintains strong structural connectivity with other structurally well-connected nodes.",
                            supporting_evidence=[],
                            provenance=f"Derived from {node_count} nodes and {edge_count} relationships in the operational graph."
                        )
                    )
                )
        except Exception as e:
            logger.warning(f"PageRank failed to converge: {e}")
            
        # -- Betweenness Centrality (Undirected) --
        try:
            bw = nx.betweenness_centrality(G_undir, weight="distance")
            sorted_bw = sorted(bw.items(), key=lambda x: (-x[1], x[0]))
            if sorted_bw and sorted_bw[0][1] > 0:
                top_bw_node, top_bw_score = sorted_bw[0]
                key_entities_list.append(
                    KeyEntity(
                        entity_id=top_bw_node,
                        metric="Betweenness",
                        score=top_bw_score,
                        explanation=Explanation(
                            what="Critical Bridge",
                            why="This entity acts as a critical structural bridge along shortest paths between other network clusters.",
                            supporting_evidence=[],
                            provenance=f"Derived from {node_count} nodes and {edge_count} relationships in the operational graph."
                        )
                    )
                )
        except Exception as e:
            logger.warning(f"Betweenness failed: {e}")
            
        # -- Communities (Louvain on Undirected) --
        communities_list = []
        try:
            # Using seed=42 for deterministic output
            louvain_comms = louvain_communities(G_undir, weight="weight", seed=42)
            
            # Sort communities by size desc, then smallest member id asc (for deterministic sorting)
            louvain_comms_sorted = sorted(
                louvain_comms, 
                key=lambda c: (-len(c), sorted(list(c))[0] if c else "")
            )
            
            for i, comm_nodes in enumerate(louvain_comms_sorted):
                comm_nodes_list = sorted(list(comm_nodes))
                # Central entity of this community (e.g. highest degree within community)
                # To be purely deterministic and structurally sound, use the node with highest degree in G_undir among members
                # tie-broken by ID
                if not comm_nodes_list:
                    continue
                central = min(comm_nodes_list, key=lambda n: (-G_undir.degree(n, weight="weight"), n))
                
                communities_list.append(
                    Community(
                        community_id=i + 1,
                        size=len(comm_nodes_list),
                        central_entity_id=central,
                        member_ids=comm_nodes_list,
                        explanation=Explanation(
                            what="Dense Sub-Network",
                            why="Nodes in this group exhibit high structural modularity and interconnectedness compared to the global graph.",
                            supporting_evidence=[],
                            provenance=f"Derived from {node_count} nodes and {edge_count} relationships in the operational graph."
                        )
                    )
                )
                
        except Exception as e:
            logger.warning(f"Louvain communities failed: {e}")
            
        # Sort key entities deterministically by metric name then id
        key_entities_list = sorted(key_entities_list, key=lambda k: (k.metric, k.entity_id))
            
        return {
            "case_id": case_id,
            "node_count": node_count,
            "edge_count": edge_count,
            "key_entities": key_entities_list,
            "communities": communities_list
        }
