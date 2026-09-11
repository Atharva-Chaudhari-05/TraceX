from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'tracex_dev_password'))

cases = [
    'CASE-01591','CASE-00394','CASE-01744','CASE-00184','CASE-00529',
    'CASE-00959','CASE-01084','CASE-01664','CASE-00564','CASE-01209',
    'CASE-01334','CASE-01594','CASE-00349','CASE-01269','CASE-01994',
    'CASE-00139','CASE-01519','CASE-01124','CASE-01059','CASE-01584',
]

with driver.session() as s:
    r = s.run('MATCH (n) WHERE n.id IN $ids RETURN n.id, labels(n)', ids=cases)
    found = r.data()
    print('Found in Neo4j:', len(found))
    for row in found:
        print(' ', row)

    r2 = s.run('MATCH (n) RETURN count(n) as cnt')
    print('Total nodes in Neo4j:', r2.single()['cnt'])

    r3 = s.run('MATCH (n) RETURN DISTINCT labels(n) as lbl, count(n) as cnt')
    for row in r3.data():
        print(f"  Label: {row['lbl']} -> {row['cnt']}")

driver.close()
