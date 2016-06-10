from flask import jsonify
from app import app
from cassandra.cluster import Cluster


cluster = Cluster(['52.35.6.29', '52.35.6.29', '52.35.6.29', '52.24.174.234'])
session = cluster.connect('raw_data')


@app.route('/')
@app.route('/index')


def index():
  return "Hello, World!"


@app.route('/api/<userid>')
def get_email(userid):
       stmt = "SELECT * FROM sensor_raw WHERE user_id={0} ALLOW FILTERING".format(userid)
       response = session.execute(stmt)
       #response = session.execute(stmt,parameters=[userid])
       response_list = []
       for val in response:
            response_list.append(val)
       jsonresponse = [{ "User ID": x.user_id, "time": x.timestamp, "dose rate": x.rate} for x in response_list]
       return jsonify(rates=jsonresponse)
