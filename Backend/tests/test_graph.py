import pytest
import uuid
from backend.app.graph.engine import GraphEngine
from backend.app.resolution.models import ResolvedEntity, ResolvedRelationship
from neo4j.exceptions import ClientError

@pytest.fixture(scope="module")
def graph_engine():
    engine = GraphEngine()
    # Ensure schema is initialized for tests if necessary
    from backend.app.graph.schema import initialize_schema
    initialize_schema()
    
    yield engine
    
    # Cleanup Neo4j
    with engine.driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

def test_sync_resolved_entity_idempotent(graph_engine):
    entity_id = uuid.uuid4()
    
    # Mock ResolvedEntity
    entity = ResolvedEntity(
        id=entity_id,
        canonical_name="Test Person",
        canonical_label="Person",
        synthetic_flag=True,
        source_dataset="test",
        provenance_mode="synthetic",
        generation_batch_id="batch123",
        audit_reference="ref123"
    )
    
    # First sync
    graph_engine.sync_resolved_entity(entity)
    
    # Verify
    with graph_engine.driver.session() as session:
        result = session.run("MATCH (n:Person {id: $id}) RETURN n.name as name", id=str(entity_id))
        record = result.single()
        assert record is not None
        assert record["name"] == "Test Person"
        
    # Second sync (Idempotent)
    entity.canonical_name = "Updated Person"
    graph_engine.sync_resolved_entity(entity)
    
    with graph_engine.driver.session() as session:
        result = session.run("MATCH (n:Person {id: $id}) RETURN count(n) as count, collect(n.name)[0] as name", id=str(entity_id))
        record = result.single()
        assert record["count"] == 1 # Still only 1 node
        assert record["name"] == "Updated Person"

def test_sync_resolved_relationship_static(graph_engine):
    source_id = uuid.uuid4()
    target_id = uuid.uuid4()
    
    # Create nodes first
    s_entity = ResolvedEntity(id=source_id, canonical_name="S", canonical_label="Person", synthetic_flag=True, source_dataset="t", provenance_mode="t", audit_reference="r")
    t_entity = ResolvedEntity(id=target_id, canonical_name="T", canonical_label="Organisation", synthetic_flag=True, source_dataset="t", provenance_mode="t", audit_reference="r")
    graph_engine.sync_resolved_entity(s_entity)
    graph_engine.sync_resolved_entity(t_entity)
    
    # Mock Relationship
    rel = ResolvedRelationship(
        source_resolved_entity_id=source_id,
        target_resolved_entity_id=target_id,
        relationship_type="WORKS_FOR",
        synthetic_flag=True,
        source_dataset="t",
        provenance_mode="t",
        audit_reference="ref-static"
    )
    
    # Sync
    graph_engine.sync_resolved_relationship(rel)
    
    # Verify
    with graph_engine.driver.session() as session:
        result = session.run("MATCH (s {id: $s})-[r:WORKS_FOR]->(t {id: $t}) RETURN r", s=str(source_id), t=str(target_id))
        record = result.single()
        assert record is not None
        
    # Second Sync (Idempotent for static)
    graph_engine.sync_resolved_relationship(rel)
    with graph_engine.driver.session() as session:
        result = session.run("MATCH (s {id: $s})-[r:WORKS_FOR]->(t {id: $t}) RETURN count(r) as count", s=str(source_id), t=str(target_id))
        assert result.single()["count"] == 1

def test_sync_resolved_relationship_event(graph_engine):
    source_id = uuid.uuid4()
    target_id = uuid.uuid4()
    
    # Create nodes first
    s_entity = ResolvedEntity(id=source_id, canonical_name="S", canonical_label="Phone", synthetic_flag=True, source_dataset="t", provenance_mode="t", audit_reference="r")
    t_entity = ResolvedEntity(id=target_id, canonical_name="T", canonical_label="Phone", synthetic_flag=True, source_dataset="t", provenance_mode="t", audit_reference="r")
    graph_engine.sync_resolved_entity(s_entity)
    graph_engine.sync_resolved_entity(t_entity)
    
    # Mock Relationship 1
    rel1 = ResolvedRelationship(
        source_resolved_entity_id=source_id,
        target_resolved_entity_id=target_id,
        relationship_type="COMMUNICATES_WITH",
        synthetic_flag=True,
        source_dataset="t",
        provenance_mode="t",
        audit_reference="event-ref-1" # Distinct event
    )
    graph_engine.sync_resolved_relationship(rel1)
    
    # Mock Relationship 2 (same pair, different event)
    rel2 = ResolvedRelationship(
        source_resolved_entity_id=source_id,
        target_resolved_entity_id=target_id,
        relationship_type="COMMUNICATES_WITH",
        synthetic_flag=True,
        source_dataset="t",
        provenance_mode="t",
        audit_reference="event-ref-2" # Distinct event
    )
    graph_engine.sync_resolved_relationship(rel2)
    
    # Verify separate events are preserved
    with graph_engine.driver.session() as session:
        result = session.run("MATCH (s {id: $s})-[r:COMMUNICATES_WITH]->(t {id: $t}) RETURN count(r) as count", s=str(source_id), t=str(target_id))
        assert result.single()["count"] == 2

def test_neighborhood_traversal_bounds(graph_engine):
    # Setup chain A -> B -> C -> D
    nodes = [uuid.uuid4() for _ in range(4)]
    for n in nodes:
        graph_engine.sync_resolved_entity(ResolvedEntity(id=n, canonical_name="N", canonical_label="Person", synthetic_flag=True, source_dataset="t", provenance_mode="t", audit_reference="r"))
        
    graph_engine.sync_resolved_relationship(ResolvedRelationship(source_resolved_entity_id=nodes[0], target_resolved_entity_id=nodes[1], relationship_type="ASSOCIATED_WITH", synthetic_flag=True, source_dataset="t", provenance_mode="t", audit_reference="r1"))
    graph_engine.sync_resolved_relationship(ResolvedRelationship(source_resolved_entity_id=nodes[1], target_resolved_entity_id=nodes[2], relationship_type="ASSOCIATED_WITH", synthetic_flag=True, source_dataset="t", provenance_mode="t", audit_reference="r2"))
    graph_engine.sync_resolved_relationship(ResolvedRelationship(source_resolved_entity_id=nodes[2], target_resolved_entity_id=nodes[3], relationship_type="ASSOCIATED_WITH", synthetic_flag=True, source_dataset="t", provenance_mode="t", audit_reference="r3"))
    
    # get_neighborhood depth is fixed to 1-hop in our query structure: MATCH (n)-[r]-(m)
    # limit=1 limits the result size
    result = graph_engine.get_neighborhood(str(nodes[1]), limit=1)
    # nodes[1] is connected to nodes[0] and nodes[2] (2 edges total). 
    # With limit 1, it should return 1 edge.
    assert len(result["edges"]) == 1

def test_sync_resolved_relationship_unsupported(graph_engine):
    source_id = uuid.uuid4()
    target_id = uuid.uuid4()
    
    # Mock Relationship with unsupported type
    rel = ResolvedRelationship(
        source_resolved_entity_id=source_id,
        target_resolved_entity_id=target_id,
        relationship_type="UNSUPPORTED_TYPE",
        synthetic_flag=True,
        source_dataset="t",
        provenance_mode="t",
        audit_reference="ref-unsupported"
    )
    
    # Sync should raise ValueError
    with pytest.raises(ValueError, match="Unsupported relationship type"):
        graph_engine.sync_resolved_relationship(rel)

def test_sync_resolved_relationship_missing_audit_ref(graph_engine):
    source_id = uuid.uuid4()
    target_id = uuid.uuid4()
    
    # Mock Event Relationship without Audit_Reference
    rel = ResolvedRelationship(
        source_resolved_entity_id=source_id,
        target_resolved_entity_id=target_id,
        relationship_type="COMMUNICATES_WITH",
        synthetic_flag=True,
        source_dataset="t",
        provenance_mode="t",
        audit_reference="" # Missing/empty audit reference
    )
    
    # Sync should raise ValueError
    with pytest.raises(ValueError, match="Missing Audit_Reference"):
        graph_engine.sync_resolved_relationship(rel)
