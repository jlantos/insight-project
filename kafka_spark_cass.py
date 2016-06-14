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

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: kafka_wordcount.py <zk> <sensor_topic> <room_topic>", file=sys.stderr)
        exit(-1)

    sc = SparkContext(appName="PythonStreamingKafkaWordCount")
    ssc = StreamingContext(sc, 1)

    zkQuorum, topic1, topic2 = sys.argv[1:]
    sensor_data = KafkaUtils.createStream(ssc, zkQuorum, "spark-streaming-consumer", {topic1: 2})
    #loc_data = KafkaUtils.createStream(ssc, zkQuorum, "spark-streaming-consumer", {topic2: 2})
    
    sensor_data.pprint()
    
      # raw_sensor = sensor_data.map(lambda (k,v): json.loads(v))
    raw_sensor = sensor_data.map(lambda k: json.loads(k[1]))
    raw_sensor.pprint()

    raw_sensor = raw_sensor.map(lambda x: json.loads(x[x.keys()[0]]))
    raw_sensor.pprint() 
    print(type(raw_sensor))
    sensor_info = raw_sensor.map(lambda x: { "user_id": x["sensor"]["userid"], "timestamp": x["sensor"]["timestamp"],  "rate": x["sensor"]["doserate"]})
    sensor_info.pprint()
    
    sensor_info.saveToCassandra("raw_data", "sensor_raw")


    ssc.start()
    ssc.awaitTermination()
