from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'tracex_dev_password'))
print(driver.session().run('MATCH (n) RETURN count(n)').single()[0])
