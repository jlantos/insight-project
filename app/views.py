from flask import jsonify
from flask import render_template
from app import app
from cassandra.cluster import Cluster
from flask import make_response
import json
from neo4jrestclient.client import GraphDatabase


cluster = Cluster(['52.35.6.29', '52.35.6.29', '52.35.6.29', '52.24.174.234'])
session = cluster.connect('rate_data')


@app.route('/')
@app.route('/index')


def index():
  user = { 'nickname': 'Miguel' } # fake user
  mylist = [1,2,3,4]
  return render_template("index.html", title = 'Home', user = user, mylist = mylist)


@app.route('/api/user_rate/<userid>')
def get_user_rate(userid):
       stmt = "SELECT * FROM user_rate WHERE user_id={0} ALLOW FILTERING".format(userid)
       response = session.execute(stmt)  
       response_list = []
       for val in response:
            response_list.append(val)
      
       jsonresponse = [{"time": x.timestamp, "dose_rate": x.rate} for x in response_list]
       return render_template("line_graph_rate.html", jsondata = (json.dumps(jsonresponse))) 
      

@app.route('/api/room_rate/<userid>')
def get_room_rate(userid):
       stmt = "SELECT * FROM room_rate WHERE room_id={0} ALLOW FILTERING".format(userid)
       response = session.execute(stmt)
       response_list = []
       for val in response:
            response_list.append(val)

       jsonresponse = [{"time": x.timestamp, "dose_rate": x.rate} for x in response_list]
       return render_template("line_graph_rate.html", jsondata = (json.dumps(jsonresponse)))


@app.route('/api/user/<userid>')
def get_user_sum(userid):
       stmt = "SELECT * FROM user_sum WHERE user_id={0} ALLOW FILTERING".format(userid)
       response = session.execute(stmt)
       response_list = []
       for val in response:
            response_list.append(val)

       jsonresponse = [{"time": x.timestamp, "dose_rate": x.sum_rate} for x in response_list]
       return render_template("line_graph_sum.html", jsondata = (json.dumps(jsonresponse)))


@app.route('/api/room/<userid>')
def get_room_sum(userid):
       stmt = "SELECT * FROM room_sum WHERE room_id={0} ALLOW FILTERING".format(userid)
       response = session.execute(stmt)
       response_list = []
       for val in response:
            response_list.append(val)

       jsonresponse = [{"time": x.timestamp, "dose_rate": x.sum_rate} for x in response_list]
       return render_template("line_graph_sum.html", jsondata = (json.dumps(jsonresponse)))


@app.route('/api/room_notification/<num_rooms>')
def get_room_alerts(num_rooms):
       db = GraphDatabase("http://ec2-52-40-124-21.us-west-2.compute.amazonaws.com:7474")
       
       dose_list = []
       times = []

       for room in range(0, int(num_rooms)):
         # Query last sum value for each room
         stmt = "SELECT * FROM room_sum WHERE room_id={0} LIMIT 1 ALLOW FILTERING".format(room)
         response = session.execute(stmt)
         # Convert Cassandra response to ROW list
         response_list = []
         for val in response:
            response_list.append(val)
         print response_list
         #if response["sum_rate"] > 80:
         #   first = "$MATCH (room { number:'" + str(room) "'})-[:GATE]-(first_con) RETURN first_con"
         #   second = "$MATCH (room { number:'" + str(room) "'})-[:GATE*2]-(sec_con) RETURN room, sec_con"

         #   results = db.query(first, returns=(str))
         #   for r in results:
         #     print(r[0])

         dose_list.append(response_list[0].sum_rate)
         times.append(response_list[0].timestamp)

       avg_time = sum(times) / (len(times))
       most_active_room =  dose_list.index(max(dose_list))
 
       jsonresponse = [{"avg_time": avg_time, "hot_room": most_active_room, "time": times, "dose_rate": dose_list}] # for x in response_list]
       return jsonify(rates=jsonresponse)


