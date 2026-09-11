import sys
import os
import argparse

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.postgres import SessionLocal
from backend.app.graph.engine import GraphEngine
from backend.app.ingestion.models import CanonicalNodeRecord, CanonicalRelationshipRecord

def run_projection(batch_id: str = None, chunk_size: int = 10000):
    """
    Standalone explicit projection execution.
    Owned by M6. Projects Canonical PostgreSQL records into Neo4j graph.
    """
    print(f"Starting M6 Graph Projection (chunk_size={chunk_size})...")
    graph_engine = GraphEngine()
    
    with SessionLocal() as db:
        print("Projecting canonical nodes from PostgreSQL...")
        
        node_query = db.query(CanonicalNodeRecord).order_by(CanonicalNodeRecord.id)
        if batch_id:
            node_query = node_query.filter_by(batch_id=batch_id)
            
        nodes_iterator = node_query.yield_per(chunk_size)
        
        node_count = 0
        node_chunk = []
        for node_record in nodes_iterator:
            payload = node_record.payload.copy()
            payload["canonical_label"] = node_record.canonical_label
            if node_record.event_type:
                payload["event_type"] = node_record.event_type
                
            node_chunk.append(payload)
            
            if len(node_chunk) >= chunk_size:
                try:
                    graph_engine.bulk_sync_canonical_nodes(node_chunk)
                    node_count += len(node_chunk)
                    print(f"Projected {node_count} nodes...")
                except Exception as e:
                    print(f"Failed to project node chunk: {e}")
                node_chunk = []
                
        # Process remaining node chunk
        if node_chunk:
            try:
                graph_engine.bulk_sync_canonical_nodes(node_chunk)
                node_count += len(node_chunk)
                print(f"Projected {node_count} nodes...")
            except Exception as e:
                print(f"Failed to project final node chunk: {e}")

        print("Projecting canonical relationships from PostgreSQL...")
        
        edge_query = db.query(CanonicalRelationshipRecord).order_by(CanonicalRelationshipRecord.id)
        if batch_id:
            edge_query = edge_query.filter_by(batch_id=batch_id)
            
        edges_iterator = edge_query.yield_per(chunk_size)
        
        edge_count = 0
        edge_chunk = []
        for edge_record in edges_iterator:
            payload = edge_record.payload.copy()
            payload["relationship_type"] = edge_record.relationship_type
            payload["source_id"] = edge_record.source_id
            payload["target_id"] = edge_record.target_id
            
            edge_chunk.append(payload)
            
            if len(edge_chunk) >= chunk_size:
                try:
                    graph_engine.bulk_sync_canonical_relationships(edge_chunk)
                    edge_count += len(edge_chunk)
                    print(f"Projected {edge_count} relationships...")
                except Exception as e:
                    print(f"Failed to project relationship chunk: {e}")
                edge_chunk = []
                
        # Process remaining edge chunk
        if edge_chunk:
            try:
                graph_engine.bulk_sync_canonical_relationships(edge_chunk)
                edge_count += len(edge_chunk)
                print(f"Projected {edge_count} relationships...")
            except Exception as e:
                print(f"Failed to project final relationship chunk: {e}")
                
        print(f"Projection complete. {node_count} nodes, {edge_count} relationships projected.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TraceX M6 Graph Projection CLI")
    parser.add_argument("--batch-id", default=None, help="Optional specific ingestion batch ID to project")
    parser.add_argument("--chunk-size", type=int, default=10000, help="Number of records to project per batch")
    args = parser.parse_args()
    
    run_projection(args.batch_id, args.chunk_size)
