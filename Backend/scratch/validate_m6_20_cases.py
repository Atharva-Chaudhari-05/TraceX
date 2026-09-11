from backend.app.graph.engine import GraphEngine

CASES = [
    "CASE-01591", "CASE-00394", "CASE-01744", "CASE-00184",
    "CASE-00529", "CASE-00959", "CASE-01084", "CASE-01664",
    "CASE-00564", "CASE-01209", "CASE-01334", "CASE-01594",
    "CASE-00349", "CASE-01269", "CASE-01994", "CASE-00139",
    "CASE-01519", "CASE-01124", "CASE-01059", "CASE-01584",
]

print("========================================")
print("M6 - 20 CASE GRAPH VERIFICATION")
print("========================================")

engine = GraphEngine()

with engine.driver.session() as session:

    node_count = session.run(
        "MATCH (n) RETURN count(n) AS count"
    ).single()["count"]

    rel_count = session.run(
        "MATCH ()-[r]->() RETURN count(r) AS count"
    ).single()["count"]

    case_count = session.run(
        "MATCH (c:Case) RETURN count(c) AS count"
    ).single()["count"]

    involved_count = session.run(
        "MATCH ()-[r:INVOLVED_IN]->() RETURN count(r) AS count"
    ).single()["count"]

    print("\nGlobal Neo4j state:")
    print(f"  Nodes          : {node_count}")
    print(f"  Relationships  : {rel_count}")
    print(f"  Case nodes     : {case_count}")
    print(f"  INVOLVED_IN    : {involved_count}")

    print("\nPer-case graph coverage:")

    passed = 0

    for case_id in CASES:

        result = session.run(
            """
            MATCH (c:Case {id: $case_id})
            OPTIONAL MATCH (c)-[r]-(n)
            WITH c,
                 count(DISTINCT n) AS neighbors,
                 count(DISTINCT r) AS relationships
            OPTIONAL MATCH (c)-[ir:INVOLVED_IN]-(p)
            RETURN
                count(DISTINCT c) AS case_exists,
                neighbors,
                relationships,
                count(DISTINCT p) AS involved_entities
            """,
            case_id=case_id,
        ).single()

        exists = result["case_exists"]
        neighbors = result["neighbors"]
        relationships = result["relationships"]
        involved = result["involved_entities"]

        if exists == 1 and neighbors > 0 and relationships > 0:
            print(
                f"  {case_id}: PASS | "
                f"neighbors={neighbors} | "
                f"relationships={relationships} | "
                f"INVOLVED_IN={involved}"
            )
            passed += 1
        else:
            print(
                f"  {case_id}: FAIL | "
                f"exists={exists} | "
                f"neighbors={neighbors} | "
                f"relationships={relationships} | "
                f"INVOLVED_IN={involved}"
            )

    print("\n========================================")
    print(f"20-CASE GRAPH COVERAGE: {passed}/20")
    print("========================================")

    if (
        passed == 20
        and node_count == 2262
        and rel_count == 3651
        and case_count == 20
        and involved_count == 40
    ):
        print("M6 20-CASE VERIFICATION: PASS")
    else:
        print("M6 20-CASE VERIFICATION: CHECK REQUIRED")
