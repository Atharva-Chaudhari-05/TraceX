import json
from backend.app.core.neo4j import driver

def main():
    case_id = "CASE-01591"
    query = """
    MATCH (c:Case {id: $case_id})-[*1..2]-(n)
    WHERE 'Event' IN labels(n) OR 'transaction' IN labels(n) OR n.canonical_label = 'Event' OR n.type = 'transaction'
    RETURN count(n) as cnt
    """
    with driver.session() as session:
        res = session.run(query, case_id=case_id)
        print("Events/Transactions connected to CASE-01591:", res.single()["cnt"])

if __name__ == "__main__":
    main()
