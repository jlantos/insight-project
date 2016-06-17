from neo4jrestclient.client import GraphDatabase


db = GraphDatabase("http://ec2-52-40-124-21.us-west-2.compute.amazonaws.com:7474") #, username="neo4j", password="mypassword")

#q = 'MATCH (u:User)-[r:likes]->(m:Beer) WHERE u.name="Marco" RETURN u, type(r), m'

q = "MATCH (martin:room { number:'1'}),(oliver:room { number:'99' }), p = shortestPath((martin)-[*..150]-(oliver)) RETURN length(p)"
# "db" as defined above

results = db.query(q, returns=(str))
for r in results:
    print(r[0])
#print(results)
