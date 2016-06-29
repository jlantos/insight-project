from neo4jrestclient.client import GraphDatabase
import time
import numpy as np

def insert_to_dict(edges, first_tag, second_tag):
  """Insert first_tag:second_tag to edges dict by either adding
     a new key, or adding second_tag to first_tag's value list"""
  if first_tag in edges:
    edges[first_tag].append(second_tag)
  else:
    edges[first_tag] = [second_tag]

  return edges


def measure_time(n, nodes, db):
  """ Measures response time for shortest distance queries """
  distance_time = []

  for i in range(1, n):
    if i%1000 == 0:
      print i

    q = "MATCH (martin:person%s {uid:'0'}),(oliver:person%s {uid: '%s' }), p = shortestPath((martin)-[*..150]-(oliver)) \
         RETURN length(p) as l" % (str(nodes), str(nodes), str(i))

    # Queary Neo4j
    start_time = time.time()
    results = db.query(q, returns=(str))
    elapsed_time = time.time() - start_time

    # Append request time
    for r in results:
      if (r[0]):
        distance_time.append((r[0], elapsed_time))
      else:
        distance_time.append((-1, elapsed_time))

  return distance_time


# Neo4j database
db = GraphDatabase("http://ec2-52-40-124-21.us-west-2.compute.amazonaws.com:7474")

node_num = 1000
samples = 100

# Measure the calc time samples times
distance_time = measure_time(samples, node_num, db)

# Group results by path length
times = {}
for i in range(0, len(distance_time)):
  insert_to_dict(times, distance_time[i][0], distance_time[i][1])

# Calc and output average time per path length
f = open('times_%s_%s' %(node_num, samples),'w')
for i in times.keys():
   f.write('%s,%s\n' % (i, np.mean(times[i])))
f.close

