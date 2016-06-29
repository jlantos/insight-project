"""
Processes 2 streams of sensor data from Kafka and pushes 
the joined and integrated values to Cassandra

Usage: kafka_spark_cass.py <zk> <topic1> <topic2>

/usr/local/spark/bin/spark-submit --master spark://ip-172-31-1-101:7077 --executor-memory 4000M --driver-memory 4000M 
--packages org.apache.spark:spark-streaming-kafka_2.10:1.6.1,TargetHolding/pyspark-cassandra:0.3.5 --conf spark.cassandra.connection.host=52.41.123.24,52.36.29.21,52.41.189.217 kafka_spark_cass.py localhost:2181 drate_18 loc_18
"""

from __future__ import print_function

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark_cassandra import streaming
import pyspark_cassandra, sys
import json

from pyspark.sql.functions import sum
from pyspark.sql.types import *
from pyspark.sql import Window
from pyspark.sql import SQLContext 
from pyspark.sql import functions


def raw_data_tojson(sensor_data):
  """ Parse input json stream """
  raw_sensor = sensor_data.map(lambda k: json.loads(k[1]))
  return(raw_sensor.map(lambda x: json.loads(x[x.keys()[0]])))
  

def main():
    """ Joins two input streams to get location specidic rates,
        integrates the rates in a sliding window to calculate qum quantity,
        saves the results to Cassandra """

    if len(sys.argv) != 4:
        print("Usage: kafka_wordcount.py <zk> <sensor_topic> <room_topic>", file=sys.stderr)
        exit(-1)

    # Kafka and Spark Streaming specific vars
    sc = SparkContext(appName="PythonStreamingRadiAction")
    ssc = StreamingContext(sc, 1)
    ssc.checkpoint("hdfs://ec2-52-24-174-234.us-west-2.compute.amazonaws.com:9000/usr/sp_data")

    zkQuorum, topic1, topic2 = sys.argv[1:]
    kafkaBrokers = {"metadata.broker.list": "52.35.6.29:9092, 52.41.24.92:9092, 52.41.26.121:9092, 52.24.174.234:9092"}
    
    # Get the sensor and location data streams
    sensor_data = KafkaUtils.createDirectStream(ssc, [topic1], kafkaBrokers)
    loc_data = KafkaUtils.createDirectStream(ssc, [topic2], kafkaBrokers)

  
    ##### Merge streams and push rates to Cassandra #####

    # Get location (room) info for users
    raw_loc = raw_data_tojson(loc_data)

    # Get sensor rate info for users
    raw_sensor = raw_data_tojson(sensor_data)
    
    # Map the 2 streams to ((userid, time), value) then join the streams
    s1 = raw_loc.map(lambda x: ((x["room"]["uid"], x["room"]["t"]) , x["room"]["nl"]))
    s2 = raw_sensor.map(lambda x: ((x["sens"]["uid"], x["sens"]["t"]), x["sens"]["dr"]))
  
    combined_info = s1.join(s2)

    # Group stream by room and calc average rate signal 
    room_rate_gen = combined_info.map(lambda x: ((x[1][0],x[0][1]), x[1][1])).groupByKey().\
                              map(lambda x : (x[0][0], (x[0][1], reduce(lambda x, y: x + y, list(x[1]))/float(len(list(x[1]))))))
  
    room_rate = room_rate_gen.map(lambda x: {"room_id": x[0], "timestamp": x[1][0], "rate": x[1][1]})
    room_rate.saveToCassandra("rate_data", "room_rate")

    # Find which users are at a certain room
    room_users = combined_info.map(lambda x: ((x[1][0],x[0][1]), x[0][0])).groupByKey().\
                               map(lambda x : {"room_id": x[0][0], "timestamp": x[0][1], "users": list(x[1])})    
    room_users.saveToCassandra("rate_data", "room_users")
  

    # Save all user info (id, time, rate, room) to Cassandra
    user_rate = combined_info.map(lambda x: { "user_id": x[0][0], "timestamp": x[0][1],  "rate": x[1][1], "room": x[1][0]})
    user_rate.saveToCassandra("rate_data", "user_rate")

    
    ##### Calculate sums for the user_rate and room_rate streams
    # Data points to sum   
    sum_time_window = 20

    # Selects all data points in window, if less than limit, calcs sum based on available average 
    def filter_list(points):
      max_time = max(points)[0]
      valid_points = [(point[1]) for point in points if (max_time - point[0]) < sum_time_window]

      return(valid_points)

    ### Find the min time for each user in the past xxx time
    user_rate_values = combined_info.map(lambda x: (x[0][0], (x[0][1], x[1][1]))) 

    def costum_add(l):
      res = 0
      length = 0
      for i in l:
        res = res + i
        length = length + 1
      if length:
        res = float(res)/length*sum_time_window
      return res 

    # Calculate user dose in sliding window
    windowed_user_rate = user_rate_values.groupByKeyAndWindow(50, 1).map(lambda x : (x[0], list(x[1]))).map(lambda x: {"user_id": x[0], "timestamp": max(x[1])[0], "sum_rate": costum_add(list(filter_list(x[1])))})
 #   windowed_user_rate.pprint()
    windowed_user_rate.saveToCassandra("rate_data", "user_sum")


    # Calculate room dose in sliding window
    windowed_room_rate = room_rate_gen.groupByKeyAndWindow(50, 1).map(lambda x : (x[0], list(x[1]))).map(lambda x: {"room_id": x[0], "timestamp": min(x[1])[0], "sum_rate": costum_add(list(filter_list(x[1])))})
    windowed_room_rate.saveToCassandra("rate_data", "room_sum")


    ssc.start()
    ssc.awaitTermination()

if __name__ == '__main__':
  main()
