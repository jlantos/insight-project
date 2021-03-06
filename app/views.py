from flask import jsonify
from flask import render_template
from app import app
from cassandra.cluster import Cluster
from flask import make_response
import json
from neo4jrestclient.client import GraphDatabase
import numpy as np

# Cassandra cluster
cluster = Cluster(['52.33.51.8', '52.33.51.8', '52.35.232.125'])
session = cluster.connect('rate_data')


@app.route('/')
@app.route('/index')
def index():
   return render_template("index.html")


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


def query_cass(stmt):
  response = session.execute(stmt)  
  response_list = []
  for val in response:
    response_list.append(val)
  return response_list


def calc_histogram(dose_list):
  """ Calc histogram, return sqrt(freq) """
  frequency, dose_value = np.histogram(dose_list, bins = range(0,  np.max(dose_list)+10))
  histogram_data = []
  for i in range(0, len(frequency)):
    histogram_data.append({"value": dose_value[i], "freq": frequency[i]**0.5})

  return histogram_data

@app.route('/api/user_rate/<userid>')
def get_user_rate(userid):
  """ Get rate time series for user """
  stmt = "SELECT * FROM user_rate WHERE user_id={0} ALLOW FILTERING".format(userid)
  
  response_list = query_cass(stmt)    
  jsonresponse = [{"time": x.timestamp, "dose_rate": x.rate} for x in response_list]
  return render_template("line_graph_rate.html", jsondata = (json.dumps(jsonresponse))) 
      

@app.route('/api/room_rate/<userid>')
def get_room_rate(userid):
  """ Get rate time series for room """
  stmt = "SELECT * FROM room_rate WHERE room_id={0} ALLOW FILTERING".format(userid)
 
  response_list = query_cass(stmt)    
  jsonresponse = [{"time": x.timestamp, "dose_rate": x.rate} for x in response_list]
  return render_template("line_graph_rate.html", jsondata = (json.dumps(jsonresponse)))


@app.route('/api/user/<userid>')
def get_user_sum(userid):
  """ Get sum time series for user """
  stmt = "SELECT * FROM user_sum WHERE user_id={0} LIMIT 50 ALLOW FILTERING".format(userid)

  response_list = query_cass(stmt)    
  jsonresponse = [{"time": x.timestamp, "dose": int(np.round(x.sum_rate))} for x in response_list]
  return(jsonresponse)


@app.route('/api/room/<userid>')
def get_room_sum(userid):
  """ Get sum time series for room """
  stmt = "SELECT * FROM room_sum WHERE room_id={0} LIMIT 50 ALLOW FILTERING".format(userid)

  response_list = query_cass(stmt)    
  jsonresponse = [{"time": (x.timestamp), "dose": int(np.round(x.sum_rate))} for x in response_list]
  return(jsonresponse)


@app.route('/api/room_notification/<num_rooms>')
def get_room_alerts(num_rooms):
  """ Calculate room specific graph data (dose distribution and time series 
      of hottest room), and users to notify """
  db = GraphDatabase("http://ec2-52-40-124-21.us-west-2.compute.amazonaws.com:7474")
  
  dose_list = []
  times = []
  alerts = []

  room_alert_threshold = 90

  # Get latest dose for all rooms
  for room in range(0, int(num_rooms)):
    # Query last sum value for each room
    stmt = "SELECT * FROM room_sum WHERE room_id={0} LIMIT 1 ALLOW FILTERING".format(room)
    response_list = query_cass(stmt)    
   
    # If room dose is higher than limit fetch users in <= 2 distance
    if (len(response_list) > 0 and response_list[0].sum_rate > room_alert_threshold):
      neighbours = [room]
      users_to_alert = []
 
      # Find first and second adjacent rooms
      first = "MATCH (room" + str(num_rooms) + "{ number :'" + str(room) + "'})-[:GATE" + str(num_rooms) + "]-(first_con) RETURN first_con.number as number"
      second = "MATCH (room" + str(num_rooms) + " { number :'" + str(room) + "'})-[:GATE" + str(num_rooms) + "*2]-(sec_con) RETURN sec_con.number as number"
      
      results = db.query(first, returns=(int))
      for r in results:
        neighbours.append(r[0])
        
      results = db.query(second, returns=(int))
      for r in results:
        neighbours.append(r[0])
      #print neighbours

      # Get the users located in the adjecent room
      for neighbour in neighbours:
        stmt = "SELECT users FROM room_users WHERE room_id = " + str(neighbour) + " AND timestamp = " + str(response_list[0].timestamp) + ";"
        response2 = session.execute(stmt)
        for val in response2:
          users_to_alert = users_to_alert+ val[0]
      # print response_list[0].timestamp, users_to_alert      
      alert = {"room": room, "users_to_alert": users_to_alert, "alert_time": response_list[0].timestamp}
      alerts.append(alert)
  
    dose_list.append(int(response_list[0].sum_rate))
    times.append(response_list[0].timestamp)

  # Find average time of last events and hottest room
  avg_time = sum(times) / (len(times))
  most_active_room =  dose_list.index(max(dose_list))
  
  # Get time series for the hottest room
  hottest_room_values = get_room_sum(most_active_room)
  
  # Create data for d3 force-directed graph
  room_file = str(num_rooms) + "_rooms"
  force_graph_data = {"nodes": create_room_values(dose_list), "links": create_room_links(room_file)}

  # Calculate histogram of dose values
  histogram_data = calc_histogram(dose_list)
      
  # Output json  
  jsonresponse = {"avg_time": avg_time, "hottest_room": most_active_room, "hottest_room_values": hottest_room_values,
              "alerts": alerts, "dose": dose_list, "dose_rates": histogram_data, "force_graph": force_graph_data}
  return jsonify(jsonresponse)


@app.route('/api/user_notification/<num_users>_<num_rooms>')
def get_user_alerts(num_users, num_rooms):
  """ Calculate room specific graph data (dose distribution and time series 
      of hottest room), and users to notify """
  db = GraphDatabase("http://ec2-52-40-124-21.us-west-2.compute.amazonaws.com:7474")

  dose_list = []
  times = []
  alerts = []

  user_alert_threshold = 300

  # Get latest dose for all users
  for user in range(0, int(num_users)):

    # Query last sum value for each room
    stmt = "SELECT * FROM user_sum WHERE user_id={0} LIMIT 1 ALLOW FILTERING".format(user)
    response_list = query_cass(stmt)    

    # If user dose is higher than limit find closest direct colleague
    if (len(response_list) > 0 and response_list[0].sum_rate > user_alert_threshold):
      connections = []
      path_lengths = []

      curr_loc_req = "SELECT room FROM user_rate WHERE user_id = " + str(user) + " AND timestamp = " + str(response_list[0].timestamp) + ";"
      curr_resp_list = query_cass(curr_loc_req)
      dang_user_room = curr_resp_list[0].room
     
      # Fetch direct colleagues
      first = "MATCH (person { uid:'" + str(user) + "'})-[:COL" + str(num_users) + "]-(first_con) RETURN first_con.uid as uid"    
      results = db.query(first, returns=(int))
      for r in results:
        connections.append(r[0])
      
      # Look up the location (room number) of the direct colleagues and calculate shortest distance
      for connection in connections:
        stmt = "SELECT room FROM user_rate WHERE user_id = " + str(connection) + " AND timestamp = " + str(response_list[0].timestamp) + ";"
        response_list_2 = query_cass(stmt) 
        
        if len(response_list_2) > 0:
          con_room = response_list_2[0].room
        else:
          con_room = -1
 
        # Find shortest path distance to each colleague
        # Handle similar room numbers as well
        if con_room <> dang_user_room:
          dist = "MATCH (u1:room"+ str(num_rooms) + "{ number:'" + str(dang_user_room) + "'}),(u2:room" + str(num_rooms) + " { number:'" + str(con_room) +"' }), \
                p = shortestPath((u1)-[*..150]-(u2)) RETURN length(p) as length"
          results = db.query(dist, returns=(int))

          if results:
            for r in results:
              path_lengths.append(r[0])
          else:
              path_lengths.append(150)
        else:
            path_lengths.append(0)
     
      # Select the one in the shortest distance
      colleague_to_notify = connections[path_lengths.index(min(path_lengths))]        

      alert = {"user_in_danger": user, "user_to_alert": colleague_to_notify, "alert_time": response_list[0].timestamp, "distance": min(path_lengths)}
      alerts.append(alert)


    dose_list.append(response_list[0].sum_rate)
    times.append(response_list[0].timestamp)

  # Find average time of last events and most exposed user
  avg_time = sum(times) / (len(times))
  most_active_user =  dose_list.index(max(dose_list))

  # Get time series for most exposed user
  most_active_user_values = get_user_sum(most_active_user)

  # Calculate histogram of dose values
  histogram_data = calc_histogram(dose_list)

  # Output json
  jsonresponse = {"avg_time": avg_time, "hottest_user": most_active_user, "hottest_user_values": most_active_user_values,
                   "alerts": alerts, "dose_rates": histogram_data}
  return jsonify(jsonresponse)

