from flask import jsonify
from flask import render_template
from app import app
from cassandra.cluster import Cluster
from flask import make_response
import json
from neo4jrestclient.client import GraphDatabase
import numpy as np

cluster = Cluster(['52.41.123.24', '52.36.29.21', '52.41.189.217'])
session = cluster.connect('rate_data')



@app.route('/')
@app.route('/index')
def index():
   return render_template("index.html")


#@app.route('/')
@app.route('/monitor')

def monitor():
 return render_template("graphs.html")


def create_room_links(filename):
  """ Reads a csv file with the "room1, room2" edges
      and converts the lines to a list of json """

  myfile = open(filename, "r")
  link_list = []

  # Process input line by line
  for line in myfile:
    rooms = line.strip().split(',')
    link_list.append({"source" : int(rooms[0]), "target" : int(rooms[1]), "value" : 1})

  myfile.close()
  return(link_list)


def create_room_values(dose_list):
  """ Turns dose list to json """
  room_list = []
  for room in range(0, len(dose_list)): 
    room_list.append({"name" : room, "dose": dose_list[room]})

  return room_list



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
       stmt = "SELECT * FROM user_sum WHERE user_id={0} LIMIT 50 ALLOW FILTERING".format(userid)
       response = session.execute(stmt)
       response_list = []
       for val in response:
            response_list.append(val)

       jsonresponse = [{"time": x.timestamp, "dose": int(np.round(x.sum_rate))} for x in response_list]
       #return render_template("line_graph_sum.html", jsondata = (json.dumps(jsonresponse)))
       return(jsonresponse)

@app.route('/api/room/<userid>')
def get_room_sum(userid):
       stmt = "SELECT * FROM room_sum WHERE room_id={0} LIMIT 50 ALLOW FILTERING".format(userid)
       response = session.execute(stmt)
       response_list = []
       for val in response:
            response_list.append(val)

       jsonresponse = [{"time": (x.timestamp), "dose": int(np.round(x.sum_rate))} for x in response_list]
#       jsonresponse = [{"time": x.timestamp, "year": str(x.timestamp), "dose_rate": x.sum_rate, "sale": str(np.round(x.sum_rate))} for x in response_list]
       #return render_template("line_graph_sum.html", jsondata = (json.dumps(jsonresponse)))
##       return(json.dumps(jsonresponse))
       return(jsonresponse)


@app.route('/api/room_notification/<num_rooms>', methods=['GET','POST'])
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
         if response_list[0].sum_rate > 90:
           neighbours = []
           users_to_alert = []
 
           first = "MATCH (room" + str(num_rooms) + "{ number :'" + str(room) + "'})-[:GATE" + str(num_rooms) + "]-(first_con) RETURN first_con.number as number"
           second = "MATCH (room" + str(num_rooms) + " { number :'" + str(room) + "'})-[:GATE" + str(num_rooms) + "*2]-(sec_con) RETURN sec_con.number as number"
           
           #print first 
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
  
         dose_list.append(int(response_list[0].sum_rate))
         times.append(response_list[0].timestamp)

       avg_time = sum(times) / (len(times))
       most_active_room =  dose_list.index(max(dose_list))
       
       hottest_room_values = get_room_sum(most_active_room)
       
       # Create data for d3 force-directed graph
       room_file = str(num_rooms) + "_rooms"
       force_graph_data = {"nodes": create_room_values(dose_list), "links": create_room_links(room_file)}

       # Calculate histogram of dose values
       frequency, dose_value = np.histogram(dose_list, bins = range(0,  np.max(dose_list)+10))#np.min(dose_list), np.max(dose_list)+2))
       histogram_data = []
       #print dose_value
       #print frequency
       for i in range(0, len(frequency)):
         histogram_data.append({"value": dose_value[i], "freq": frequency[i]})
      
       #with open('force_graph_data', 'w') as outfile:
       #  json.dump(force_graph_data, outfile)
       #return render_template("force_graph_renderer.html", jsondata = (json.dumps(force_graph_data)))


       jsonresponse = {"avg_time": avg_time, "hottest_room": most_active_room, "hottest_room_values": hottest_room_values,
                        "alerts": alerts, "dose": dose_list, "dose_rates": histogram_data, "force_graph": force_graph_data} # for x in response_list]
       return jsonify(jsonresponse)


@app.route('/api/user_notification/<num_users>_<num_rooms>')
def get_user_alerts(num_users, num_rooms):
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
<<<<<<< HEAD
         if response_list[0].sum_rate > 120:
=======
         if (len(response_list) > 0 and response_list[0].sum_rate > 300):
>>>>>>> 626ef69655b5830ed5a2c039c2543b03c52c60bf
           connections = []
           path_lengths = []

           curr_loc_req = "SELECT room FROM user_rate WHERE user_id = " + str(user) + " AND timestamp = " + str(response_list[0].timestamp) + ";"
           curr_resp = session.execute(curr_loc_req)
           # Convert Cassandra response to ROW list
           curr_resp_list = []
           for val in curr_resp:
             curr_resp_list.append(val[0])
           dang_user_room = curr_resp_list[0]
          
           #print dang_user_room

 
           # Fetch direct colleagues
           first = "MATCH (person { uid:'" + str(user) + "'})-[:COL" + str(num_users) + "]-(first_con) RETURN first_con.uid as uid"
           
           results = db.query(first, returns=(int))
           for r in results:
             connections.append(r[0])
              
           ####print connections
           # Look up the location (room number) of the direct colleagues and calculate shortest distance
           for connection in connections:
             stmt = "SELECT room FROM user_rate WHERE user_id = " + str(connection) + " AND timestamp = " + str(response_list[0].timestamp) + ";"
             response2 = session.execute(stmt)
            # Convert Cassandra response to ROW list
             response_list_2 = []
             for val in response2:
               response_list_2.append(val[0])
             con_room = response_list_2[0]
             ####print con_room  
             # Find shortest path distance to each colleagues
             # Handle similar room numbers as well
             if con_room <> dang_user_room:
               dist = "MATCH (u1:room"+ str(num_rooms) + "{ number:'" + str(dang_user_room) + "'}),(u2:room" + str(num_rooms) + " { number:'" + str(con_room) +"' }), \
                     p = shortestPath((u1)-[*..150]-(u2)) RETURN length(p) as length"
 
               results = db.query(dist, returns=(int))
               for r in results:
                 path_lengths.append(r[0])
             else:
                 path_lengths.append(0)
           
           # Select the one in the shortest distance
           colleague_to_notify = connections[path_lengths.index(min(path_lengths))]             

           alert = {"user_in_danger": user, "user_to_alert": colleague_to_notify, "distance": min(path_lengths)}
           alerts.append(alert)


         dose_list.append(response_list[0].sum_rate)
         times.append(response_list[0].timestamp)

       avg_time = sum(times) / (len(times))
       most_active_user =  dose_list.index(max(dose_list))

       most_active_user_values = get_user_sum(most_active_user)

       # Calculate histogram of dose values
       frequency, dose_value = np.histogram(dose_list, bins = range(0,  np.max(dose_list)+10))#np.min(dose_list), np.max(dose_list)+2))
       histogram_data = []
       for i in range(0, len(frequency)):
         if frequency[i] > 0:
           histogram_data.append({"value": dose_value[i], "freq": frequency[i]})
         else:
           histogram_data.append({"value": dose_value[i], "freq": 1})


       jsonresponse = {"avg_time": avg_time, "hottest_user": most_active_user, "hottest_user_values": most_active_user_values,
                        "alerts": alerts, "dose_rates": histogram_data}
       return jsonify(jsonresponse)

