import time
import sys
import random
import json


def insert_to_dict(edges, first_tag, second_tag):
  """ Inserts elements to dictionary 1->2, 2->1 """
  if first_tag in edges:
    edges[first_tag].append(second_tag)
  else:
    edges[first_tag] = [second_tag]

  return edges


def create_room_dict(filename):
  """ Reads a csv file with the "room1, room2" edges
      and converts the lines to a dict """

  myfile = open(filename, "r")
  room_dict = {}

  for line in myfile:
    rooms = line.strip().split(',')
    # Both room get the other as a value
    insert_to_dict(room_dict, int(rooms[0]), int(rooms[1]))
    insert_to_dict(room_dict, int(rooms[1]), int(rooms[0]))

  myfile.close()

  return room_dict


def main():
  """Simulates sensor and location data (both in the same and 
     in 2 separate streams)."""
  if len(sys.argv) != 4:
    print "Usage: ./create_data.py #users #rooms full_time_mins"
    sys.exit(1)

  n_users = int(sys.argv[1])
  n_rooms = int(sys.argv[2])
  time_length = int(sys.argv[3])

  # Output for sensor and location datastream
  #badge_output = open('badge_stream_all', "w")
  #sensor_output = open('sensor_stream_all', "w")
  output_filename = 'badge_sensor_stream_all' + sys.argv[1] + '_' + sys.argv[2]
  badge_sensor_output = open(output_filename, "w")

  # Set random state
  random.seed(1)

  ## Pre-defined graph for the rooms (r=10)
  #rooms = (dict([(0, [1, 2, 3]), (1, [0, 4]), (2, [0, 5]), (3, [0, 5]), (4, [1, 7]), 
  #         (5, [2, 3, 6]), (6, [5, 7]), (7, [4, 6, 8, 9]), (8, [7]), (9, [7])]))

  room_filename = sys.argv[2] + '_rooms'
  rooms = create_room_dict(room_filename)
  print rooms

  # Rate values
  background = 1
  normal_work = 9
  contamination = 5

  old_location = [-1] * n_users
  
  # Time starts at 0 and ends time_length mins later
  for t in range(0, time_length):
    # Follow the n users
    for user_id in range (0, n_users):

      location_changed = False

      ### Select room ###
      # Initial location is randomly selected
      if t == 0: 
        new_location = random.randint(0, n_rooms-1)
        location_changed = True
      else:
        # User changes room twice per hour in average
        if random.random() < 2.0/60:
          new_location = rooms[old_location[user_id]][random.randint(0,len(rooms[old_location[user_id]])-1)]
          location_changed = True
        # Or stays in the same room
        else:
          new_location = old_location[user_id]

      ### Calculating dose rate ###
      # Dose rate is normal except in room 6 after 240 min
      #if (new_location == 6 and t > 120 and t < 400) or (new_location == 96 and t > 500 and t < 800):
      if (new_location == 6 and t > 20 and t < 60) or (new_location == 96 and t > 70 and t < 110):
        rate = contamination
      else:
        rate = background
      # Once per hour the employees get extra dose from work
      if random.random() < 1.0/60:
        rate = rate + normal_work
      # User exceeds limit in a certain time range
      #if (user_id == 123 and t > 10 and t < 200):
      #  rate = rate + normal_work * 3
      if (user_id == 123 and t > 10 and t < 40):
        rate = rate + normal_work * 2
   
      #loc_data = {"room": {"userid": user_id,  "timestamp": t, "newloc": new_location, "oldloc": old_location[user_id]}}
      #sens_data = {"sensor": {"userid": user_id,  "timestamp": t, "doserate": rate}}

      loc_data = {"room": {"uid": user_id,  "t": t, "nl": new_location, "ol": old_location[user_id]}}
      sens_data = {"sens": {"uid": user_id,  "t": t, "dr": rate}}
     
      location_changed = True
      # Write the info for this minute to file
      if location_changed:   
        #json.dump(loc_data, badge_output)
        #badge_output.write("\n")

        json.dump(loc_data, badge_sensor_output)
        badge_sensor_output.write("\n")

      #json.dump(sens_data, sensor_output)
      #sensor_output.write("\n")

      json.dump(sens_data, badge_sensor_output)
      badge_sensor_output.write("\n")

      # Keep track of previous room
      old_location[user_id] = new_location
      # print t, user_id, new_location, rate


  # Send everybody home
  new_location = -1
  t = t + 1
  for user_id in range (0, n_users):
    loc_data = {"room": {"uid": user_id,  "t": t, "nl": new_location, "ol": old_location[user_id]}}
    #json.dump(loc_data, badge_output)
    #badge_output.write("\n")

    json.dump(loc_data, badge_sensor_output)
    badge_sensor_output.write("\n")
  


  # Close files
  #badge_output.close()
  #sensor_output.close()
  badge_sensor_output.close()


# Timing run
start_time = time.time()

if __name__ == "__main__":
  main()

print("--- Running time: %.3f seconds ---" % (time.time() - start_time))
