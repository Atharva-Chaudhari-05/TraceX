import logging
from typing import Dict, Any, List
from neo4j import Transaction

from backend.app.core.neo4j import driver
from backend.app.resolution.models import ResolvedEntity, ResolvedRelationship

logger = logging.getLogger(__name__)

# TraceX Relationship Definitions
STATIC_RELATIONSHIPS = {
    "ASSOCIATED_WITH", "HAS_DOCUMENT", "HAS_EVENT", "INVOLVED_IN",
    "LOCATED_AT", "OWNS", "USES", "WORKS_FOR"
}

EVENT_RELATIONSHIPS = {
    "COMMUNICATES_WITH", "CONNECTED_TO", "PARTICIPATED_IN", "TRANSFERRED_TO"
}

class GraphEngine:
    def __init__(self):
        self.driver = driver

    def _get_canonical_id(self, record: dict, label: str) -> str:
        """Extracts the specific source ID and maps it to canonical graph 'id'."""
        id_fields = [
            "id", "person_id", "phone_id", "account_id", "location_id",
            "organization_id", "vehicle_id", "device_id", "document_id",
            "case_id", "transaction_id", "communication_id",
            "network_event_id", "physical_event_id", "incident_id"
        ]
        for f in id_fields:
            if f in record and record[f] is not None:
                return str(record[f])
        return record.get("Audit_Reference", "UNKNOWN_ID")

    def _merge_node(self, tx: Transaction, label: str, node_id: str, props: Dict[str, Any]):
        """Idempotent MERGE for nodes."""
        props["id"] = node_id
        
        # Cypher labels must be sanitized
        if not label.isalnum():
            raise ValueError(f"Invalid label: {label}")
            
        query = f"""
        MERGE (n:{label} {{id: $node_id}})
        SET n += $props
        """
        tx.run(query, node_id=node_id, props=props)

    def sync_canonical_node(self, canonical_node: Any):
        """Sync M3 CanonicalNode (direct from ingestion)."""
        record_dict = canonical_node.model_dump()
        label = record_dict.pop("canonical_label")
        
        # Event subtype logic
        sub_label = None
        if label == "Event" and "event_type" in record_dict:
            sub_label = record_dict.pop("event_type")
        
        node_id = self._get_canonical_id(record_dict, label)
        
        with self.driver.session() as session:
            session.execute_write(self._merge_node, label, node_id, record_dict)
            if sub_label:
                # Add subtype label
                session.execute_write(
                    lambda tx: tx.run(f"MATCH (n:{label} {{id: $id}}) SET n:{sub_label}", id=node_id)
                )

    def _merge_static_relationship(self, tx: Transaction, source_id: str, rel_type: str, target_id: str, props: dict):
        if not rel_type.replace('_', '').isalnum():
            raise ValueError(f"Invalid relationship type: {rel_type}")
            
        query = f"""
        MATCH (s {{id: $source_id}}), (t {{id: $target_id}})
        MERGE (s)-[r:{rel_type}]->(t)
        SET r += $props
        """
        tx.run(query, source_id=source_id, target_id=target_id, props=props)

    def _merge_event_relationship(self, tx: Transaction, source_id: str, rel_type: str, target_id: str, props: dict):
        if not rel_type.replace('_', '').isalnum():
            raise ValueError(f"Invalid relationship type: {rel_type}")
            
        audit_ref = props.get("Audit_Reference")
        if not audit_ref:
            raise ValueError(f"Missing Audit_Reference for event relationship: {rel_type}")
        # Handle timestamp safely if present
        timestamp = props.get("timestamp", None)
        
        query = f"""
        MATCH (s {{id: $source_id}}), (t {{id: $target_id}})
        MERGE (s)-[r:{rel_type} {{Audit_Reference: $audit_ref}}]->(t)
        SET r += $props
        """
        tx.run(query, source_id=source_id, target_id=target_id, audit_ref=audit_ref, props=props)

    def sync_canonical_relationship(self, rel: Any):
        """Sync M3 CanonicalRelationship."""
        props = rel.model_dump()
        rel_type = props.pop("relationship_type")
        source_id = props.pop("source_id")
        target_id = props.pop("target_id")
        
        # Serialize datetime
        if "timestamp" in props and props["timestamp"]:
            props["timestamp"] = props["timestamp"].isoformat()
        
        with self.driver.session() as session:
            if rel_type in STATIC_RELATIONSHIPS:
                session.execute_write(self._merge_static_relationship, str(source_id), rel_type, str(target_id), props)
            elif rel_type in EVENT_RELATIONSHIPS:
                session.execute_write(self._merge_event_relationship, str(source_id), rel_type, str(target_id), props)
            else:
                raise ValueError(f"Unsupported relationship type: {rel_type}")

    def bulk_sync_canonical_nodes(self, nodes_payloads: List[Dict]):
        from collections import defaultdict
        
        groups = defaultdict(list)
        for record_dict in nodes_payloads:
            label = record_dict.pop("canonical_label")
            if not label.isalnum():
                raise ValueError(f"Invalid label: {label}")
                
            sub_label = None
            if label == "Event" and "event_type" in record_dict:
                sub_label = record_dict.pop("event_type")
                if sub_label and not sub_label.isalnum():
                    raise ValueError(f"Invalid sub_label: {sub_label}")
                    
            node_id = self._get_canonical_id(record_dict, label)
            record_dict["id"] = node_id
            
            groups[(label, sub_label)].append(record_dict)
            
        with self.driver.session() as session:
            for (label, sub_label), records in groups.items():
                query = f"""
                UNWIND $records AS record
                MERGE (n:{label} {{id: record.id}})
                SET n += record
                """
                if sub_label:
                    query += f"\nSET n:{sub_label}"
                
                session.execute_write(lambda tx, q, recs: tx.run(q, records=recs), query, records)

    def bulk_sync_canonical_relationships(self, rels_payloads: List[Dict]):
        from collections import defaultdict
        import datetime
        
        groups = defaultdict(list)
        for props in rels_payloads:
            rel_type = props.pop("relationship_type")
            if not rel_type.replace('_', '').isalnum():
                raise ValueError(f"Invalid relationship type: {rel_type}")
                
            source_id = props.pop("source_id")
            target_id = props.pop("target_id")
            
            if "timestamp" in props and props["timestamp"]:
                if hasattr(props["timestamp"], "isoformat"):
                    props["timestamp"] = props["timestamp"].isoformat()
                else:
                    props["timestamp"] = str(props["timestamp"])
            
            record = {
                "source_id": str(source_id),
                "target_id": str(target_id),
                "props": props
            }
            
            is_event = rel_type in EVENT_RELATIONSHIPS
            is_static = rel_type in STATIC_RELATIONSHIPS
            
            if not is_event and not is_static:
                raise ValueError(f"Unsupported relationship type: {rel_type}")
                
            if is_event:
                audit_ref = props.get("Audit_Reference")
                if not audit_ref:
                    raise ValueError(f"Missing Audit_Reference for event relationship: {rel_type}")
                record["audit_ref"] = audit_ref
                
            groups[(rel_type, is_event)].append(record)
            
        with self.driver.session() as session:
            for (rel_type, is_event), records in groups.items():
                if is_event:
                    query = f"""
                    UNWIND $records AS record
                    MERGE (s {{id: record.source_id}})
                    MERGE (t {{id: record.target_id}})
                    MERGE (s)-[r:{rel_type} {{Audit_Reference: record.audit_ref}}]->(t)
                    SET r += record.props
                    """
                else:
                    query = f"""
                    UNWIND $records AS record
                    MERGE (s {{id: record.source_id}})
                    MERGE (t {{id: record.target_id}})
                    MERGE (s)-[r:{rel_type}]->(t)
                    SET r += record.props
                    """
                session.execute_write(lambda tx, q, recs: tx.run(q, records=recs), query, records)

    def sync_resolved_entity(self, resolved_entity: ResolvedEntity):
        """Sync M5 confirmed ResolvedEntity to Neo4j."""
        label = resolved_entity.canonical_label
        node_id = str(resolved_entity.id)
        
        props = {
            "name": resolved_entity.canonical_name,
            "Synthetic_Flag": resolved_entity.synthetic_flag,
            "Source_Dataset": resolved_entity.source_dataset,
            "Provenance_Mode": resolved_entity.provenance_mode,
            "Generation_Batch_ID": resolved_entity.generation_batch_id,
            "Audit_Reference": resolved_entity.audit_reference,
            "source_record_reference": None
        }
        
        try:
            with self.driver.session() as session:
                session.execute_write(self._merge_node, label, node_id, props)
        except Exception as e:
            logger.error(f"Neo4j sync failed for ResolvedEntity {node_id}: {e}")
            raise RuntimeError("Graph Sync Failed")

    def sync_resolved_relationship(self, resolved_relationship: ResolvedRelationship):
        """Sync M5 confirmed ResolvedRelationship to Neo4j."""
        source_id = str(resolved_relationship.source_resolved_entity_id)
        target_id = str(resolved_relationship.target_resolved_entity_id)
        rel_type = resolved_relationship.relationship_type
        
        props = {
            "Synthetic_Flag": resolved_relationship.synthetic_flag,
            "Source_Dataset": resolved_relationship.source_dataset,
            "Provenance_Mode": resolved_relationship.provenance_mode,
            "Generation_Batch_ID": resolved_relationship.generation_batch_id,
            "Audit_Reference": resolved_relationship.audit_reference,
            "source_record_reference": None
        }
        
        try:
            with self.driver.session() as session:
                if rel_type in STATIC_RELATIONSHIPS:
                    session.execute_write(self._merge_static_relationship, source_id, rel_type, target_id, props)
                elif rel_type in EVENT_RELATIONSHIPS:
                    session.execute_write(self._merge_event_relationship, source_id, rel_type, target_id, props)
                else:
                    raise ValueError(f"Unsupported relationship type: {rel_type}")
        except ValueError as ve:
            logger.error(f"Validation failed for ResolvedRelationship {resolved_relationship.id}: {ve}")
            raise ve
        except Exception as e:
            logger.error(f"Neo4j sync failed for ResolvedRelationship {resolved_relationship.id}: {e}")
            raise RuntimeError("Graph Sync Failed")

    def get_neighborhood(self, node_id: str, depth: int = 1, limit: int = 100) -> Dict[str, List]:
        """Bounded traversal of ego-graph neighborhood."""
        query = f"""
        MATCH p = (n {{id: $node_id}})-[*1..{depth}]-(m)
        WITH p LIMIT $limit
        UNWIND relationships(p) AS r
        RETURN startNode(r) AS n, r, endNode(r) AS m
        """
        nodes = {}
        edges = []
        
        with self.driver.session() as session:
            result = session.run(query, node_id=node_id, limit=limit)
            for record in result:
                n = record["n"]
                m = record["m"]
                r = record["r"]
                
                if n["id"] not in nodes:
                    nodes[n["id"]] = {"id": n["id"], "labels": list(n.labels), "properties": dict(n)}
                if m["id"] not in nodes:
                    nodes[m["id"]] = {"id": m["id"], "labels": list(m.labels), "properties": dict(m)}
                    
                edges.append({
                    "id": r.element_id,
                    "source": r.nodes[0]["id"],
                    "target": r.nodes[1]["id"],
                    "type": r.type,
                    "properties": dict(r)
                })
                
        return {"nodes": list(nodes.values()), "edges": edges}

    def get_shortest_path(self, source_id: str, target_id: str, max_depth: int = 4, limit: int = 5) -> Dict[str, List]:
        """Bounded shortest path traversal."""
        query = f"""
        MATCH p = shortestPath((s {{id: $source_id}})-[*..{max_depth}]-(t {{id: $target_id}}))
        RETURN p LIMIT $limit
        """
        nodes = {}
        edges = []
        
        with self.driver.session() as session:
            result = session.run(query, source_id=source_id, target_id=target_id, limit=limit)
            for record in result:
                path = record["p"]
                for node in path.nodes:
                    if node["id"] not in nodes:
                        nodes[node["id"]] = {"id": node["id"], "labels": list(node.labels), "properties": dict(node)}
                for rel in path.relationships:
                    edges.append({
                        "id": rel.element_id,
                        "source": rel.nodes[0]["id"],
                        "target": rel.nodes[1]["id"],
                        "type": rel.type,
                        "properties": dict(rel)
                    })
                    
        return {"nodes": list(nodes.values()), "edges": edges}

    def extract_case_subgraph(self, case_id: str, max_nodes: int = 5000, max_edges: int = 20000) -> Dict[str, Any]:
        """
        Extract a case-scoped subgraph from Neo4j for M7 Network Analytics.
        Returns nodes and edges up to MAX + 1 to allow overflow detection (sentinel logic).
        """
        # Node limit logic: Find all nodes connected to the case, and their neighbors.
        # For simplicity in MVP, we just match (c:Case {id: $case_id})-[:INVOLVED_IN*1..3]-(n)
        # But wait, TraceX Schema says: Nodes are INVOLVED_IN a case. Or nodes are LOCATED_AT etc.
        # Let's do a broad neighborhood fetch from nodes explicitly INVOLVED_IN the case.
        # Actually, simpler: fetch all nodes directly INVOLVED_IN the Case, plus their 1-hop connections.
        
        query = f"""
        // 1. Anchor on the case and find all directly involved nodes
        MATCH (c {{id: $case_id}})<-[:INVOLVED_IN]-(core)
        WITH core
        // 2. Find 1-hop neighborhood for all core nodes
        OPTIONAL MATCH (core)-[r]-(neighbor)
        
        WITH collect(DISTINCT core) + collect(DISTINCT neighbor) AS all_nodes,
             collect(DISTINCT r) AS all_edges
             
        UNWIND all_nodes AS n
        WITH DISTINCT n, all_edges LIMIT {max_nodes + 1}
        WITH collect(n) AS nodes, all_edges
        
        UNWIND all_edges AS e
        WITH nodes, e LIMIT {max_edges + 1}
        WITH nodes, collect(e) AS edges
        
        RETURN nodes, edges
        """
        
        # A simpler fallback query if the above is too convoluted:
        query_simple = f"""
        MATCH (c {{id: $case_id}})<-[:INVOLVED_IN]-(core)
        WITH collect(DISTINCT core) AS core_nodes
        
        // Unwind and get 1-hop
        UNWIND core_nodes AS n
        OPTIONAL MATCH (n)-[r]-(m)
        
        // Distinct edges
        WITH core_nodes, collect(DISTINCT r) AS edges
        
        // Distinct all nodes
        UNWIND edges AS e
        WITH core_nodes, startNode(e) AS s, endNode(e) AS t, e
        WITH core_nodes + collect(DISTINCT s) + collect(DISTINCT t) AS all_n, collect(DISTINCT e) AS all_e
        
        UNWIND all_n AS un_n
        WITH DISTINCT un_n AS n, all_e LIMIT {max_nodes + 1}
        WITH collect(n) AS final_nodes, all_e
        
        UNWIND all_e AS un_e
        WITH final_nodes, DISTINCT un_e AS e LIMIT {max_edges + 1}
        
        RETURN final_nodes AS nodes, collect(e) AS edges
        """
        
        # We can just fetch the whole thing directly without convoluted OPTIONAL MATCHes
        # If we just get all relationships involving ANY core node
        query_best = f"""
        MATCH (c {{id: $case_id}})<-[:INVOLVED_IN]-(core)
        MATCH (core)-[r]-(m)
        WITH collect(DISTINCT core) + collect(DISTINCT m) AS raw_nodes, collect(DISTINCT r) AS raw_edges
        
        UNWIND raw_nodes AS n
        WITH DISTINCT n, raw_edges LIMIT {max_nodes + 1}
        WITH collect(n) AS nodes, raw_edges
        
        UNWIND raw_edges AS e
        WITH DISTINCT e, nodes LIMIT {max_edges + 1}
        RETURN nodes, collect(e) AS edges
        """
        
        nodes_dict = {}
        edges_list = []
        
        with self.driver.session() as session:
            result = session.run(query_best, case_id=case_id)
            record = result.single()
            if record:
                for n in record["nodes"]:
                    nodes_dict[n["id"]] = {"id": n["id"], "labels": list(n.labels), "properties": dict(n)}
                
                for r in record["edges"]:
                    edges_list.append({
                        "id": r.element_id,
                        "source": r.nodes[0]["id"],
                        "target": r.nodes[1]["id"],
                        "type": r.type,
                        "properties": dict(r)
                    })
                    
        return {"nodes": list(nodes_dict.values()), "edges": edges_list}
