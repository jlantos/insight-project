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

from pyspark import StorageLevel

from pyspark.sql.functions import sum
from pyspark.sql.types import *
from pyspark.sql import Window
from pyspark.sql import SQLContext 
from pyspark.sql import functions


#CASSANDRA_CLUSTER_IP_LIST = [CASSANDRA_NODE1, CASSANDRA_NODE2, CASSANDRA_NODE3]


def raw_data_tojson(sensor_data):
  raw_sensor = sensor_data.map(lambda k: json.loads(k[1]))
  return(raw_sensor.map(lambda x: json.loads(x[x.keys()[0]])))
  

#def sparse_loc_data(sensor_data):
#  raw_sensor = sensor_data.map(lambda k: json.loads(k[1]))
#  raw_sensor = raw_sensor.map(lambda x: json.loads(x[x.keys()[0]]))
#  sensor_info = raw_sensor.map(lambda x: { "user_id": x["room"]["userid"], "timestamp": x["room"]["timestamp"],  "room": x["room"]["newloc"]})
#
#  return sensor_info


def main():
    if len(sys.argv) != 4:
        print("Usage: kafka_wordcount.py <zk> <sensor_topic> <room_topic>", file=sys.stderr)
        exit(-1)

    sc = SparkContext(appName="PythonStreamingKafkaWordCount")
    ssc = StreamingContext(sc, 5)
    ssc.checkpoint("hdfs://ec2-52-24-174-234.us-west-2.compute.amazonaws.com:9000/usr/sp_data")
   # sqlContext = SQLContext(sc)

    zkQuorum, topic1, topic2 = sys.argv[1:]
    # Get the sensor and location data streams
    #sensor_data = KafkaUtils.createStream(ssc, zkQuorum, "spark-streaming-consumer", {topic1: 1})
    #loc_data = KafkaUtils.createStream(ssc, zkQuorum, "spark-streaming-consumer-2", {topic2: 1})
    
    kafkaBrokers = {"metadata.broker.list": "52.35.6.29:9092, 52.41.24.92:9092, 52.41.26.121:9092, 52.24.174.234:9092"}
    sensor_data = KafkaUtils.createDirectStream(ssc, [topic1], kafkaBrokers)
    loc_data = KafkaUtils.createDirectStream(ssc, [topic2], kafkaBrokers)

    
  
    ##### Merge streams and push rates to Cassandra #####


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
    s1 = raw_loc.map(lambda x: ((x["room"]["uid"], x["room"]["t"]) , x["room"]["nl"]))
    s2 = raw_sensor.map(lambda x: ((x["sens"]["uid"], x["sens"]["t"]), x["sens"]["dr"]))
  #  s1.pprint()
  #  s2.pprint()

    combined_info = s1.join(s2).persist(StorageLevel.MEMORY_ONLY)
    #combined_info.pprint()

    # Map ((room, time), rate) then take the average of the rates
   # room_info = combined_info.map(lambda x: ((x[1][0],x[0][1]), x[1][1], x[0][0])).groupByKey().map(lambda x : (x[0], reduce(lambda x, y: x + y, list(x[1])) / len(list(x[1])), list(x[2]) ))
    
    #room_info.pprint()
    room_rate_gen = combined_info.map(lambda x: ((x[1][0],x[0][1]), x[1][1])).groupByKey().\
                              map(lambda x : (x[0][0], (x[0][1], reduce(lambda x, y: x + y, list(x[1]))/float(len(list(x[1])))))).persist(StorageLevel.MEMORY_ONLY)
  
    room_rate = room_rate_gen.map(lambda x: {"room_id": x[0], "timestamp": x[1][0], "rate": x[1][1]})
  
    #room_rate.pprint()
    room_rate.saveToCassandra("rate_data", "room_rate")

    #room_users = combined_info.map(lambda x: ((x[1][0],x[0][1]), x[0][0])).groupByKey().map(lambda x : (x[0], list(x[1])))
    room_users = combined_info.map(lambda x: ((x[1][0],x[0][1]), x[0][0])).groupByKey().\
                               map(lambda x : {"room_id": x[0][0], "timestamp": x[0][1], "users": list(x[1])})    
    #room_users.pprint()
    room_users.saveToCassandra("rate_data", "room_users")
  
    # Full info for user: id, time, rate, room
    user_rate = combined_info.map(lambda x: { "user_id": x[0][0], "timestamp": x[0][1],  "rate": x[1][1], "room": x[1][0]})
   # print(type(user_rate))
    user_rate.saveToCassandra("rate_data", "user_rate")


    
    ##### Calculate sums for the user_rate and room_rate streams
    #users = range(0, number_of_users)
    #time_last_calc = {}
    #for u in users:
    #  time_last_calc[u] = 0

    #broadcastVar = sc.broadcast(time_last_calc)

    sum_time_window = 20
    # Selects all data points in window, if less than limit, calcs sum based on available average 
    def filter_list(points):
   #   min_time = min(points)[0]
      max_time = max(points)[0]
      #return [(point[0], point[1]) for point in points if (point[0]-min_time) < sum_time_window]
#      return(sum([(point[1]) for point in points if (point[0]-min_time) < sum_time_window])/float(len(points))*20)
      valid_points = [(point[1]) for point in points if (max_time - point[0]) < sum_time_window]
#      valid_points = [(point[1]) for point in points if (point[0]-min_time) < sum_time_window]

      return(valid_points)

    ### Find the min time for each user in the past xxx time
    user_rate_values = combined_info.map(lambda x: (x[0][0], (x[0][1], x[1][1]))) 
#    windowed_user_rate = user_rate_values.window(10, 1).groupByKey().map(lambda x : (x[0], (list(x[1])))) 
#    windowed_user_rate = user_rate_values.window(10, 1).groupByKey().map(lambda x : (x[0], min(list(x[1]))))
#    windowed_user_rate = user_rate_values.window(10, 1).groupByKey().map(lambda x : (x[0], list(x[1]))).filter(lambda x: (y[0]-min(x[1])[0]) < 60 for y in x[1] )

#    windowed_user_rate = user_rate_values.window(100, 1).groupByKey().map(lambda x : (x[0], list(x[1]))).map(lambda x: (x[0], filter_list(x[1])))
 #   windowed_user_rate = user_rate_values.window(100, 1).groupByKey().map(lambda x : (x[0], list(x[1]))).map(lambda x: {"user_id": x[0], "timestamp": min(x[1])[0], "rate": filter_list(x[1])})
 #   windowed_user_rate.saveToCassandra("rata_data", "user_sum")

   # windowed_user_rate = user_rate_values.groupByKeyAndWindow(100, 1).map(lambda x : (x[0], list(x[1]))).map(lambda x: (x[0], min(x[1])[0], list(filter_list(x[1])))).map(lambda x: {"user_id": x[0], "timestamp": x[1], "rate": sum(x[2])})
    def costum_add(l):
      res = 0
      length = 0
      for i in l:
        res = res + i
        length = length + 1
      if length:
        res = float(res)/length*sum_time_window
      return res 

    windowed_user_rate = user_rate_values.groupByKeyAndWindow(50, 5).map(lambda x : (x[0], list(x[1]))).map(lambda x: {"user_id": x[0], "timestamp": max(x[1])[0], "sum_rate": costum_add(list(filter_list(x[1])))})
 #   windowed_user_rate.pprint()
    windowed_user_rate.saveToCassandra("rate_data", "user_sum")



    windowed_room_rate = room_rate_gen.groupByKeyAndWindow(50, 5).map(lambda x : (x[0], list(x[1]))).map(lambda x: {"room_id": x[0], "timestamp": min(x[1])[0], "sum_rate": costum_add(list(filter_list(x[1])))})
    windowed_room_rate.saveToCassandra("rate_data", "room_sum")


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
