from flask import jsonify
from flask import render_template
from app import app
from cassandra.cluster import Cluster
from flask import make_response
import json

cluster = Cluster(['52.35.6.29', '52.35.6.29', '52.35.6.29', '52.24.174.234'])
session = cluster.connect('rata_data')


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

