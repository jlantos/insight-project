from flask import jsonify
from flask import render_template
from app import app
from cassandra.cluster import Cluster
from flask import make_response
import json

cluster = Cluster(['52.35.6.29', '52.35.6.29', '52.35.6.29', '52.24.174.234'])
session = cluster.connect('raw_data')


@app.route('/')
@app.route('/index')


def index():
  user = { 'nickname': 'Miguel' } # fake user
  mylist = [1,2,3,4]
  return render_template("index.html", title = 'Home', user = user, mylist = mylist)


@app.route('/api/<userid>')
def get_email(userid):
       stmt = "SELECT * FROM sensor_raw WHERE user_id={0} ALLOW FILTERING".format(userid)
       response = session.execute(stmt)
       #response = session.execute(stmt,parameters=[userid])
       response_list = []
       for val in response:
            response_list.append(val)
      # jsonresponse = [{ "User ID": x.user_id, "time": x.timestamp, "dose rate": x.rate} for x in response_list]
       #return jsonify(rates=jsonresponse)
       jsonresponse = [{"time": x.timestamp, "dose_rate": x.rate} for x in response_list]
       return render_template("line_graph.html", jsondata = (json.dumps(jsonresponse))) 
       #return render_template("line_graph.html", jsondata = (jsonify(stream={"r":jsonresponse})))

