from flask import jsonify
from app import app
from cassandra.cluster import Cluster


cluster = Cluster(['52.35.6.29', '52.35.6.29', '52.35.6.29', '52.24.174.234'])
session = cluster.connect('raw_data')


@app.route('/')
@app.route('/index')


def index():
  return "Hello, World!"


@app.route('/api/<user_id>')
def get_email(user):
       stmt = "SELECT * FROM sensor_raw WHERE user_id={} ALLOW FILTERING".format(user_id)
       response = session.execute(stmt, parameters=[user_id])
       response_list = []
       for val in response:
            response_list.append(val)
       jsonresponse = [{ "User ID": x.user_id, "time": x.timestamp, "dose rate": x.rate} for x in response_list]
       return jsonify(rates=jsonresponse)
