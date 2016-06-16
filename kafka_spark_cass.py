"""
Processes 2 streams of sensor data from Kafka and pushes the joined tables
to Cassandra

 Usage: kafka_spark_cass.py <zk> <topic1> <topic2>

 /usr/local/spark/bin/spark-submit --packages org.apache.spark:spark-streaming-kafka_2.10:1.6.1,TargetHolding/pyspark-cassandra:0.3.5 kafka_spark_cass.py localhost:2181 sensor room
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


def raw_data_tojson(sensor_data):
  raw_sensor = sensor_data.map(lambda k: json.loads(k[1]))
  return(raw_sensor.map(lambda x: json.loads(x[x.keys()[0]])))
  

def sparse_loc_data(sensor_data):
  raw_sensor = sensor_data.map(lambda k: json.loads(k[1]))
  raw_sensor = raw_sensor.map(lambda x: json.loads(x[x.keys()[0]]))
  sensor_info = raw_sensor.map(lambda x: { "user_id": x["room"]["userid"], "timestamp": x["room"]["timestamp"],  "room": x["room"]["newloc"]})

  return sensor_info


def main():
    if len(sys.argv) != 4:
        print("Usage: kafka_wordcount.py <zk> <sensor_topic> <room_topic>", file=sys.stderr)
        exit(-1)

    sc = SparkContext(appName="PythonStreamingKafkaWordCount")
    ssc = StreamingContext(sc, 1)
    ssc.checkpoint("checkpoint")
    sqlContext = SQLContext(sc)

    zkQuorum, topic1, topic2 = sys.argv[1:]
    # Get the sensor and location data streams
    #sensor_data = KafkaUtils.createStream(ssc, zkQuorum, "spark-streaming-consumer", {topic1: 1})
    #loc_data = KafkaUtils.createStream(ssc, zkQuorum, "spark-streaming-consumer-2", {topic2: 1})
    
    kafkaBrokers = {"metadata.broker.list": "52.35.6.29:9092, 52.41.24.92:9092, 52.41.26.121:9092, 52.24.174.234:9092"}
    sensor_data = KafkaUtils.createDirectStream(ssc, [topic1], kafkaBrokers)
    loc_data = KafkaUtils.createDirectStream(ssc, [topic2], kafkaBrokers)

    ## RDD with initial state (key, value) pairs
    #initialStateRDD = sc.parallelize([(0, 100), (1, 100)])    
    
    #def updateFunc(new_values, last_room):
    #    return(new_values or last_room or 100)

    raw_loc = raw_data_tojson(loc_data)
  ##  loc_info = raw_loc.map(lambda x: { "user_id": x["room"]["userid"], "timestamp": x["room"]["timestamp"],  "room": x["room"]["newloc"]})
    #loc_info.pprint()
  ##  loc_info.saveToCassandra("raw_data", "loc_raw")

    #running_rooms = loc_info.map(lambda x: x['room']).updateStateByKey(updateFunc)
    #running_rooms.pprint()

    raw_sensor = raw_data_tojson(sensor_data)
  ##  sensor_info = raw_sensor.map(lambda x: { "user_id": x["sensor"]["userid"], "timestamp": x["sensor"]["timestamp"],  "rate": x["sensor"]["doserate"]})
    #sensor_info.pprint()
  ##  sensor_info.saveToCassandra("raw_data", "sensor_raw")
    
    # Map the 2 streams to ((userid, time), value) then join the streams
    s1 = raw_loc.map(lambda x: ((x["room"]["userid"], x["room"]["timestamp"]) , x["room"]["newloc"]))
    s2 = raw_sensor.map(lambda x: ((x["sensor"]["userid"], x["sensor"]["timestamp"]), x["sensor"]["doserate"]))
    #s1.pprint()
    #s2.pprint()

    combined_info = s1.join(s2)
    #combined_info.pprint()

    # Map ((room, time), rate) then take the average of the rates
   # room_info = combined_info.map(lambda x: ((x[1][0],x[0][1]), x[1][1], x[0][0])).groupByKey().map(lambda x : (x[0], reduce(lambda x, y: x + y, list(x[1])) / len(list(x[1])), list(x[2]) ))
    
    #room_info.pprint()
    room_rate = combined_info.map(lambda x: ((x[1][0],x[0][1]), x[1][1])).groupByKey().\
                              map(lambda x : {"room_id": x[0][0], "timestamp": x[0][1], "rate": reduce(lambda x, y: x + y, list(x[1]))/float(len(list(x[1])))} )
    #room_rate.pprint()
    room_rate.saveToCassandra("rata_data", "room_rate")

    #room_users = combined_info.map(lambda x: ((x[1][0],x[0][1]), x[0][0])).groupByKey().map(lambda x : (x[0], list(x[1])))
    room_users = combined_info.map(lambda x: ((x[1][0],x[0][1]), x[0][0])).groupByKey().\
                               map(lambda x : {"room_id": x[0][0], "timestamp": x[0][1], "users": list(x[1])})    
    #room_users.pprint()
    room_users.saveToCassandra("rata_data", "room_users")
  
    # Full info for user: id, time, rate, room
    user_rate = combined_info.map(lambda x: { "user_id": x[0][0], "timestamp": x[0][1],  "rate": x[1][1], "room": x[1][0]})
    #user_rate.pprint()
    user_rate.saveToCassandra("rata_data", "user_rate")


    # Calculate rate sum for the last 60 timeclocks
    #window = Window.partitionBy("id").orderBy("time").rowsBetween(-60, 0)
    #room_rate_2 = room_rate.map(lambda x: (x[0][0], x[0][1], x[1][0]))
    #room_rate_2.pprint()
    #df_room = sqlContext.createDataFrame(room_rate_2, ['id', 'time', 'rate'])
   # df_room = df_room.withColumn("rate",df_room["rate"].cast(DoubleType()).alias("rate"))
   # df_room = df_room.withColumn("time", df_room["time"].cast(IntegerType()).alias("time"))
    #df_room.show()

    ssc.start()
    ssc.awaitTermination()

if __name__ == '__main__':
  main()
