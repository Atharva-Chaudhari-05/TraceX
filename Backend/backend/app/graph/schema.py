import logging
from backend.app.core.neo4j import driver

logger = logging.getLogger(__name__)

CANONICAL_LABELS = [
    "Person", "Phone", "Account", "Location", "Organisation",
    "Vehicle", "Device", "Document", "Event", "Case"
]

def initialize_schema():
    """
    Initializes Neo4j constraints and indexes safely using a single canonical graph identity property `id`.
    """
    logger.info("Initializing Neo4j Graph Schema...")
    with driver.session() as session:
        # 1. Uniqueness constraints for canonical labels
        for label in CANONICAL_LABELS:
            # We use `id` as the single canonical graph identity property
            constraint_name = f"constraint_unique_{label.lower()}_id"
            query = f"""
            CREATE CONSTRAINT {constraint_name} IF NOT EXISTS 
            FOR (n:{label}) REQUIRE n.id IS UNIQUE
            """
            try:
                session.run(query)
            except Exception as e:
                logger.error(f"Failed to create constraint {constraint_name} for {label}: {e}")

        # 2. Single-property indexes
        indexes = {
            "Person": "name",
            "Organisation": "name",
            "Location": "name"
        }
        for label, prop in indexes.items():
            index_name = f"index_{label.lower()}_{prop}"
            query = f"""
            CREATE INDEX {index_name} IF NOT EXISTS 
            FOR (n:{label}) ON (n.{prop})
            """
            try:
                session.run(query)
            except Exception as e:
                logger.error(f"Failed to create index {index_name} for {label}: {e}")

    logger.info("Neo4j Graph Schema Initialization Complete.")
