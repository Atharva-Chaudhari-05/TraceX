import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.app.core.neo4j import driver

with driver.session() as session:
    res = session.run("MATCH (n) RETURN n.id as id, labels(n) as labels")
    for r in res:
        print(r)
