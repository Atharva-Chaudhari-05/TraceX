from backend.app.core.neo4j import driver

def main():
    with driver.session() as session:
        res = session.run("MATCH (n:Case) RETURN n LIMIT 1")
        record = res.single()
        if record:
            print("Case node:", record[0])
        else:
            print("No case node found")

if __name__ == "__main__":
    main()
