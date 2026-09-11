import pytest
from backend.app.core.postgres import Base, engine
from backend.app.graph.engine import GraphEngine

def test_audit_log_ingestion_registration():
    """
    Test that Base.metadata.create_all() does not raise NoReferencedTableError
    due to missing users table import for AuditLog's foreign key.
    """
    # This simulates what run_ingestion.py does implicitly via SQLAlchemy flush
    # or what a clean database setup would do. We just verify the table exists in metadata
    # and has the foreign key to users.id.
    
    # We ensure that AuditLog is in the metadata
    assert "audit_logs" in Base.metadata.tables
    audit_table = Base.metadata.tables["audit_logs"]
    
    # We ensure that users is in the metadata
    assert "users" in Base.metadata.tables
    
    # Check if the foreign key exists and points to users.id
    fks = list(audit_table.foreign_keys)
    assert any(fk.column.table.name == "users" for fk in fks), "AuditLog does not have a foreign key to users"


def test_graph_engine_extract_case_subgraph_cypher_syntax(mock_neo4j_driver):
    """
    Test that extract_case_subgraph generates valid Cypher without syntax errors.
    Since we don't have Neo4j running in unit tests by default, we mock the session run
    and just verify it executes without Cypher syntax errors.
    """
    engine = GraphEngine()
    engine.driver = mock_neo4j_driver
    
    engine.extract_case_subgraph(case_id="CASE-123")
    
    # Get the query that was executed
    mock_session = mock_neo4j_driver.session.return_value.__enter__.return_value
    call_args = mock_session.run.call_args
    assert call_args is not None
    
    query = call_args[0][0]
    
    # Assert that the invalid syntax is not present
    assert "WITH nodes, DISTINCT e" not in query
    
    # Assert the correct syntax is present and validate surrounding semantics
    assert "WITH DISTINCT e, nodes" in query
    
    # Validate the full semantic pipeline of the deduplication step
    import re
    
    assert re.search(r"UNWIND raw_edges AS e\s+WITH DISTINCT e, nodes LIMIT \d+\s+RETURN nodes, collect\(e\) AS edges", query), "Missing semantic pipeline for deduplication"
