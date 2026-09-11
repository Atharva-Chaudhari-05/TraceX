import sys
import os
import argparse
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.postgres import SessionLocal
from backend.app.graph.engine import GraphEngine
from backend.app.ingestion.models import (
    CanonicalNodeRecord,
    CanonicalRelationshipRecord,
)


DEFAULT_CASES = [
    "CASE-01591",
    "CASE-00394",
    "CASE-01744",
    "CASE-00184",
    "CASE-00529",
    "CASE-00959",
    "CASE-01084",
    "CASE-01664",
    "CASE-00564",
    "CASE-01209",
    "CASE-01334",
    "CASE-01594",
    "CASE-00349",
    "CASE-01269",
    "CASE-01994",
    "CASE-00139",
    "CASE-01519",
    "CASE-01124",
    "CASE-01059",
    "CASE-01584",
]

MAX_NODES = 30000
MAX_RELATIONSHIPS = 100000
CHUNK_SIZE = 5000


def build_case_subgraph(db, case_ids):
    """
    Build a bounded case-centered graph entirely from PostgreSQL.

    PostgreSQL remains the source of truth.
    Neo4j receives only the resulting bounded projection.
    """

    print(f"Selecting {len(case_ids)} cases...")

    # ------------------------------------------------------------
    # 1. Find the core entities directly involved in the cases.
    # ------------------------------------------------------------
    involved = (
        db.query(
            CanonicalRelationshipRecord.source_id,
            CanonicalRelationshipRecord.target_id,
        )
        .filter(
            CanonicalRelationshipRecord.relationship_type == "INVOLVED_IN",
            CanonicalRelationshipRecord.target_id.in_(case_ids),
        )
        .all()
    )

    core_ids = set(case_ids)

    for source_id, target_id in involved:
        if target_id in case_ids:
            core_ids.add(source_id)
            core_ids.add(target_id)

    print(f"Direct case/core entities: {len(core_ids)}")

    # ------------------------------------------------------------
    # 2. Find all relationships touching those core entities.
    # ------------------------------------------------------------
    relationships = (
        db.query(CanonicalRelationshipRecord)
        .filter(
            (
                CanonicalRelationshipRecord.source_id.in_(core_ids)
                | CanonicalRelationshipRecord.target_id.in_(core_ids)
            )
        )
        .order_by(CanonicalRelationshipRecord.id)
        .all()
    )

    print(f"Relationships touching core entities: {len(relationships)}")

    # ------------------------------------------------------------
    # 3. Expand one hop to relationship endpoints.
    # ------------------------------------------------------------
    selected_relationships = []
    selected_node_ids = set(core_ids)

    for rel in relationships:
        if len(selected_relationships) >= MAX_RELATIONSHIPS:
            print("Reached relationship safety limit.")
            break

        selected_relationships.append(rel)
        selected_node_ids.add(rel.source_id)
        selected_node_ids.add(rel.target_id)

    print(f"Selected relationships: {len(selected_relationships)}")
    print(f"Selected node IDs before node cap: {len(selected_node_ids)}")

    if len(selected_node_ids) > MAX_NODES:
        print(
            f"Node set exceeds MAX_NODES={MAX_NODES}. "
            f"Trimming deterministically."
        )

        # Always preserve selected cases.
        preserved = set(case_ids)

        remaining = sorted(
            node_id
            for node_id in selected_node_ids
            if node_id not in preserved
        )

        allowed = MAX_NODES - len(preserved)

        selected_node_ids = preserved | set(remaining[:allowed])

        # Keep only relationships whose endpoints remain.
        selected_relationships = [
            rel
            for rel in selected_relationships
            if rel.source_id in selected_node_ids
            and rel.target_id in selected_node_ids
        ]

    print(f"Final nodes: {len(selected_node_ids)}")
    print(f"Final relationships: {len(selected_relationships)}")

    return selected_node_ids, selected_relationships


def load_nodes(db, node_ids):
    """
    Load canonical node payloads for the bounded graph.
    """

    nodes = (
        db.query(CanonicalNodeRecord)
        .filter(CanonicalNodeRecord.canonical_id.in_(node_ids))
        .order_by(CanonicalNodeRecord.id)
        .all()
    )

    print(f"Loaded {len(nodes)} canonical node records.")

    return nodes


def project_nodes(graph_engine, nodes):
    node_count = 0

    chunk = []

    for node_record in nodes:
        payload = node_record.payload.copy()
        payload["canonical_label"] = node_record.canonical_label

        if node_record.event_type:
            payload["event_type"] = node_record.event_type

        chunk.append(payload)

        if len(chunk) >= CHUNK_SIZE:
            graph_engine.bulk_sync_canonical_nodes(chunk)
            node_count += len(chunk)
            print(f"Projected {node_count} nodes...")
            chunk = []

    if chunk:
        graph_engine.bulk_sync_canonical_nodes(chunk)
        node_count += len(chunk)
        print(f"Projected {node_count} nodes...")

    return node_count


def project_relationships(graph_engine, relationships):
    edge_count = 0

    chunk = []

    for rel_record in relationships:
        payload = rel_record.payload.copy()
        payload["relationship_type"] = rel_record.relationship_type
        payload["source_id"] = rel_record.source_id
        payload["target_id"] = rel_record.target_id

        chunk.append(payload)

        if len(chunk) >= CHUNK_SIZE:
            graph_engine.bulk_sync_canonical_relationships(chunk)
            edge_count += len(chunk)
            print(f"Projected {edge_count} relationships...")
            chunk = []

    if chunk:
        graph_engine.bulk_sync_canonical_relationships(chunk)
        edge_count += len(chunk)
        print(f"Projected {edge_count} relationships...")

    return edge_count


def run_demo_projection(case_ids):
    print("=" * 70)
    print("TraceX Bounded Demo Graph Projection")
    print("=" * 70)

    print(f"Cases: {', '.join(case_ids)}")
    print(f"MAX_NODES: {MAX_NODES}")
    print(f"MAX_RELATIONSHIPS: {MAX_RELATIONSHIPS}")
    print()

    graph_engine = GraphEngine()

    with SessionLocal() as db:
        node_ids, relationships = build_case_subgraph(
            db,
            case_ids,
        )

        nodes = load_nodes(db, node_ids)

        if not nodes:
            raise RuntimeError("No canonical nodes found for selected cases.")

        print()
        print("Projecting bounded nodes to Neo4j...")

        projected_nodes = project_nodes(
            graph_engine,
            nodes,
        )

        print()
        print("Projecting bounded relationships to Neo4j...")

        projected_relationships = project_relationships(
            graph_engine,
            relationships,
        )

    print()
    print("=" * 70)
    print("DEMO PROJECTION COMPLETE")
    print("=" * 70)
    print(f"Cases selected:          {len(case_ids)}")
    print(f"Nodes projected:         {projected_nodes}")
    print(f"Relationships projected: {projected_relationships}")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="TraceX bounded multi-case Neo4j demo projection"
    )

    parser.add_argument(
        "--cases",
        nargs="+",
        default=DEFAULT_CASES,
        help="Case IDs to project",
    )

    args = parser.parse_args()

    run_demo_projection(args.cases)