import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.app.core.neo4j import driver

query = """
MATCH (c {id: $case_id})<-[:INVOLVED_IN]-(core)
MATCH (core)-[r]-(m)
WITH collect(DISTINCT core) + collect(DISTINCT m) AS raw_nodes, collect(DISTINCT r) AS raw_edges

UNWIND raw_nodes AS n
WITH DISTINCT n, raw_edges LIMIT $max_nodes
WITH collect(n) AS nodes, raw_edges

UNWIND raw_edges AS e
WITH DISTINCT e, nodes LIMIT $max_edges
RETURN nodes, collect(e) AS edges
"""

with driver.session() as session:
    res = session.run(query, case_id="CASE-1", max_nodes=5000, max_edges=20000)
    record = res.single()
    print("Record:", record)
    if record:
        print("Nodes length:", len(record["nodes"]))
        print("Edges length:", len(record["edges"]))
