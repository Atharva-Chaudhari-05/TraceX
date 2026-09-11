import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.app.graph.engine import GraphEngine

graph_engine = GraphEngine()
subgraph = graph_engine.extract_case_subgraph("CASE-SMOKE-POS", max_nodes=5000, max_edges=20000)
nodes = subgraph["nodes"]
edges = subgraph["edges"]

print(f"Nodes: {len(nodes)}")
print(f"Edges: {len(edges)}")
if nodes:
    print(f"Sample node: {nodes[0]}")
if edges:
    print(f"Sample edge: {edges[0]}")
