import sys
import json
import yaml
import os
import time
from kafka import KafkaProducer


def main():
  """Reads input file and sends the lines as json to Kafka
     with optional delay between messages"""

  # Housekeeping
  if len(sys.argv) < 4:
    print "Usage: ./kafka_producer.py file_name sensor_topic room_topic"
    sys.exit(1)

  if len(sys.argv) >= 5:
    wait_time = float(sys.argv[4])
  else:
    wait_time = 0


  # Set up Producer: send to all 4 instances, encode json

  ipfile = open('ip_addresses.txt', 'r')
  ips = ipfile.read()[:-1]
  ipfile.close()
  ips = ips.split(', ')

  producer_s = (KafkaProducer(bootstrap_servers=ips, 
              value_serializer=lambda v: json.dumps(v).encode('utf-8')))

  producer_r = (KafkaProducer(bootstrap_servers=ips, 
              value_serializer=lambda v: json.dumps(v).encode('utf-8')))

  # Read the file over and over and send the messages line by line
  forever = True
  
 # while forever:
    # Open file and send the messages line by line
  with open(sys.argv[1]) as f:
      for line in f:
        d = yaml.safe_load(line)
        jd = json.dumps(d)
        # topic and message
        if 'sensor' in d:
          producer_s.send(sys.argv[2],jd)
        if 'room' in d:
          producer_r.send(sys.argv[3],jd)
        
        time.sleep(wait_time)



if __name__ == "__main__":
  main()
