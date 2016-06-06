import time
import sys
import random
import json


def main():
  """Simulates sensor and location data (in 2 spearate streams)."""
  if len(sys.argv) != 3:
    print "Usage: ./create_data.py file-to-read output-file-name"
    # sys.exit(1)

  # Output for sensor and location datastream
  badge_output = open('badge_stream', "w")
  sensor_output = open('sensor_stream', "w")

  # Set random state
  random.seed(2)

  # Pre-defined graph for the rooms (r=10)
  rooms = (dict([(0, [1, 2, 3]), (1, [0, 4]), (2, [0, 5]), (3, [0, 5]), (4, [1, 7]), 
           (5, [2, 3, 6]), (6, [5, 7]), (7, [4, 6, 8, 9]), (8, [7]), (9, [7])]))

  print rooms

  # Rate values
  background = 1
  normal_work = 9
  contamination = 5

  user_id = 1
  old_location = 100
  
  # Time starts at 0 and ends 8 hours later
  for t in range(0, 480):
    ### Select room ###
    # Initial location is randomly selected
    if t == 0: 
      new_location = random.randint(0, 9)
    else:
      # User changes room twice per hour in average
      if random.random() < 2.0/60:
        new_location = rooms[old_location][random.randint(0,len(rooms[old_location])-1)]
      # Or stays in the same room
      else:
        new_location = old_location

    ### Calculating dose rate ###
    # Dose rate is normal except in room 6 after 240 min
    if (new_location <> 6) or (t < 240):
      rate = background
    else:
      rate = contamination
    # Once per hour the employees get extra dose from work
    if random.random() < 1.0/60:
      rate = rate + normal_work
      
    loc_data = {"room": {"userid": user_id,  "timestamp": t, "newloc": new_location, "oldloc": old_location}}
    sens_data = {"sensor": {"userid": user_id,  "timestamp": t, "doserate": rate}}

    # Write the info for this minute to file   
    json.dump(loc_data, badge_output)
    badge_output.write("\n")

    json.dump(sens_data, sensor_output)
    sensor_output.write("\n")

    # Keep track of previous room
    old_location = new_location

  
  # Close files
  badge_output.close()
  sensor_output.close()


# Timing run
start_time = time.time()

if __name__ == "__main__":
  main()

print("--- Running time: %.3f seconds ---" % (time.time() - start_time))
