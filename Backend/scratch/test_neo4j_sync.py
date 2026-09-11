import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.app.core.neo4j import driver
from backend.app.graph.engine import GraphEngine
from backend.app.ingestion.schemas import Case, Person, CanonicalRelationship

graph_engine = GraphEngine()

c = Case(
    case_id="CASE-1",
    Synthetic_Flag=True,
    Source_Dataset="smoke",
    source_record_reference="ref1",
    Audit_Reference="audit1",
    Provenance_Mode="direct"
)
graph_engine.sync_canonical_node(c)

p = Person(
    person_id="PERSON-1",
    Synthetic_Flag=True,
    Source_Dataset="smoke",
    source_record_reference="ref2",
    Audit_Reference="audit2",
    Provenance_Mode="direct"
)
graph_engine.sync_canonical_node(p)

r = CanonicalRelationship(
    source_id="PERSON-1",
    target_id="CASE-1",
    relationship_type="INVOLVED_IN",
    Synthetic_Flag=True,
    Source_Dataset="smoke",
    source_record_reference="ref3",
    Audit_Reference="audit3",
    Provenance_Mode="direct"
)
graph_engine.sync_canonical_relationship(r)

with driver.session() as session:
    res = session.run("MATCH (n) RETURN n.id as id, labels(n) as labels")
    for record in res:
        print("Node:", record)
    res2 = session.run("MATCH ()-[r]->() RETURN type(r)")
    for record in res2:
        print("Edge:", record)
