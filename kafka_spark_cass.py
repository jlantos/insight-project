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
    loc_info = raw_loc.map(lambda x: { "user_id": x["room"]["userid"], "timestamp": x["room"]["timestamp"],  "room": x["room"]["newloc"]})
    #loc_info.pprint()
    loc_info.saveToCassandra("raw_data", "loc_raw")

    #running_rooms = loc_info.map(lambda x: x['room']).updateStateByKey(updateFunc)
    #running_rooms.pprint()

    raw_sensor = raw_data_tojson(sensor_data)
    sensor_info = raw_sensor.map(lambda x: { "user_id": x["sensor"]["userid"], "timestamp": x["sensor"]["timestamp"],  "rate": x["sensor"]["doserate"]})
    #sensor_info.pprint()
    sensor_info.saveToCassandra("raw_data", "sensor_raw")
    
    s1 = raw_loc.map(lambda x: ((x["room"]["userid"], x["room"]["timestamp"]) , x["room"]["newloc"]))
    #s1.pprint()
    s2 = raw_sensor.map(lambda x: ((x["sensor"]["userid"], x["sensor"]["timestamp"]), x["sensor"]["doserate"]))
    #s2.pprint()

    combined_info = s1.join(s2)
    #combined_info.pprint()
    # Map ((room, time), rate)
    room_info = combined_info.map(lambda x: ((x[1][0],x[0][1]), x[1][1])).groupByKey().map(lambda x : (x[0], list(x[1])))
    room_info.pprint()
    

    ssc.start()
    ssc.awaitTermination()

if __name__ == '__main__':
  main()
