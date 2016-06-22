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
       stmt = "SELECT * FROM room_sum WHERE room_id={0} LIMIT 50 ALLOW FILTERING".format(userid)
       response = session.execute(stmt)
       response_list = []
       for val in response:
            response_list.append(val)

       jsonresponse = [{"time": x.timestamp, "dose_rate": x.sum_rate} for x in response_list]
       #return render_template("line_graph_sum.html", jsondata = (json.dumps(jsonresponse)))
       return(json.dumps(jsonresponse))


@app.route('/api/room_notification/<num_rooms>')
def get_room_alerts(num_rooms):
       db = GraphDatabase("http://ec2-52-40-124-21.us-west-2.compute.amazonaws.com:7474")
       
       dose_list = []
       times = []
       alerts = []

       for room in range(0, int(num_rooms)):

         # Query last sum value for each room
         stmt = "SELECT * FROM room_sum WHERE room_id={0} LIMIT 1 ALLOW FILTERING".format(room)
         response = session.execute(stmt)
         # Convert Cassandra response to ROW list
         response_list = []
         for val in response:
            response_list.append(val)
         #print response_list
         
         # If room dose is higher than limit fetch users in <= 2 distance
         if response_list[0].sum_rate > 80:
           neighbours = []
           users_to_alert = []
 
           first = "MATCH (room" + str(num_rooms) + "{ number :'" + str(room) + "'})-[:GATE" + str(num_rooms) + "]-(first_con) RETURN first_con.number as number"
           second = "MATCH (room" + str(num_rooms) + " { number :'" + str(room) + "'})-[:GATE" + str(num_rooms) + "*2]-(sec_con) RETURN sec_con.number as number"
           
           print first 
           results = db.query(first, returns=(int))
           for r in results:
             neighbours.append(r[0])
             
           results = db.query(second, returns=(int))
           for r in results:
             neighbours.append(r[0])

           for neighbour in neighbours:
             #print neighbour
             #print response_list[0].timestamp
             stmt = "SELECT users FROM room_users WHERE room_id = " + str(neighbour) + " AND timestamp = " + str(response_list[0].timestamp) + ";"
             #print stmt
             response2 = session.execute(stmt)
            # Convert Cassandra response to ROW list
             response_list_2 = []
             for val in response2:
               users_to_alert = users_to_alert+ val[0]
           
           alert = {"room": room, "users_to_alert": users_to_alert}
           alerts.append(alert)
  
         dose_list.append(response_list[0].sum_rate)
         times.append(response_list[0].timestamp)

       avg_time = sum(times) / (len(times))
       most_active_room =  dose_list.index(max(dose_list))
       
       hottest_room_values = get_room_sum(most_active_room)
       
       jsonresponse = [{"avg_time": avg_time, "hottest_room": most_active_room, "hottest_room_values": hottest_room_values,
                        "alerts": alerts, "dose_rates": dose_list}] # for x in response_list]
       return jsonify(rates=jsonresponse)


@app.route('/api/user_notification/<num_users>')
def get_user_alerts(num_users):
       db = GraphDatabase("http://ec2-52-40-124-21.us-west-2.compute.amazonaws.com:7474")

       dose_list = []
       times = []
       alerts = []

       for user in range(0, int(num_users)):

         # Query last sum value for each room
         stmt = "SELECT * FROM user_sum WHERE user_id={0} LIMIT 1 ALLOW FILTERING".format(user)
         response = session.execute(stmt)
         # Convert Cassandra response to ROW list
         response_list = []
         for val in response:
            response_list.append(val)
         #print response_list

         # If room dose is higher than limit fetch users in <= 2 distance
         if response_list[0].sum_rate > 100:
           connections = []
           
           # Fetch direct colleagues
           first = "MATCH (person { uid:'" + str(user) + "'})-[:COL" + str(num_users) + "]-(first_con) RETURN first_con.uid as uid"
           
           results = db.query(first, returns=(int))
           for r in results:
             connections.append(r[0])
              
           print connections

           for connection in connections:
             stmt = "SELECT room FROM user_rate WHERE user_id = " + str(connection) + " AND timestamp = " + str(response_list[0].timestamp) + ";"
             response2 = session.execute(stmt)
            # Convert Cassandra response to ROW list
             response_list_2 = []
             for val in response2:
               response_list_2.append(val[0])

             

      #     alert = {"room": room, "users_to_alert": users_to_alert}
     #      alerts.append(alert)

         dose_list.append(response_list[0].sum_rate)
         times.append(response_list[0].timestamp)

       avg_time = sum(times) / (len(times))
       most_active_user =  dose_list.index(max(dose_list))

     #  hottest_room_values = get_room_sum(most_active_room)

       jsonresponse = [{"avg_time": avg_time, "dose_rates": dose_list}]
       return jsonify(rates=jsonresponse)

