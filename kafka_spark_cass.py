#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
 Counts words in UTF8 encoded, '\n' delimited text received from the network every second.
 Usage: kafka_wordcount.py <zk> <topic>

 To run this on your local machine, you need to setup Kafka and create a producer first, see
 http://kafka.apache.org/documentation.html#quickstart

 and then run the example
    `$ bin/spark-submit --jars \
      external/kafka-assembly/target/scala-*/spark-streaming-kafka-assembly-*.jar \
      examples/src/main/python/streaming/kafka_wordcount.py \
      localhost:2181 test`
"""
from __future__ import print_function

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark_cassandra import streaming
import pyspark_cassandra, sys
import json


def sparse_sensor_data(sensor_data):
  raw_sensor = sensor_data.map(lambda k: json.loads(k[1]))
  raw_sensor = raw_sensor.map(lambda x: json.loads(x[x.keys()[0]]))
  sensor_info = raw_sensor.map(lambda x: { "user_id": x["sensor"]["userid"], "timestamp": x["sensor"]["timestamp"],  "rate": x["sensor"]["doserate"]})

  return sensor_info

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

    zkQuorum, topic1, topic2 = sys.argv[1:]
    # Get the sensor and location data streams
    #sensor_data = KafkaUtils.createStream(ssc, zkQuorum, "spark-streaming-consumer", {topic1: 1})
    #loc_data = KafkaUtils.createStream(ssc, zkQuorum, "spark-streaming-consumer-2", {topic2: 1})
    
    kafkaBrokers = {"metadata.broker.list": "52.35.6.29:9092, 52.41.24.92:9092, 52.41.26.121:9092, 52.24.174.234:9092"}
    sensor_data = KafkaUtils.createDirectStream(ssc, [topic1], kafkaBrokers)
    loc_data = KafkaUtils.createDirectStream(ssc, [topic2], kafkaBrokers)

    
    sensor_info = sparse_sensor_data(sensor_data)
    #sensor_info.pprint()
    sensor_info.saveToCassandra("raw_data", "sensor_raw")

    loc_info = sparse_loc_data(loc_data)
    #loc_info.pprint()
    loc_info.saveToCassandra("raw_data", "loc_raw")


    ssc.start()
    ssc.awaitTermination()

if __name__ == '__main__':
  main()
