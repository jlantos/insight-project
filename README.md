# [RadiAction](https:/radiaction.site)

## Table of contents
1. [Introduction](README.md#introduction)
2. [AWS Clusters](README.md#aws-clusters) 
3. [Data Pipeline](README.md#data-pipeline)
4. [Performance](README.md#performance)
5. [Presentation](README.md#presentation)


## Introduction 
[Back to Table of contents](README.md#table-of-contents)

[RadiAction](http://radiaction.site) is a monitoring and alerting platform for health risk factors associated with time integrated quantities. It is a big data pipeline which uses personal sensor measurements for location monitoring and produces alerts based on graph relations.

As a concrete example I'm simulating a facility where employees are working with radioactive sources. Two streams of user data are collected: dose rate (from personal dosimeters) and user location (room) information. The pipeline reconstructs the room specific dose rates from the merged streams, and calculates the time integral of both user and room doses in a sliding window. 

If a user's dose exceeds the predefined limit the closest (in distance) of his direct colleagues is notified. If a room's dose is too high - hence it's considered contaminated - all users in <= 2 distance are notified.

![Alt text](pp/static/img/room_graph.png?raw=true "Room map")




## AWS Clusters
[Back to Table of contents](README.md#table-of-contents)

run.sh located in the root runs src/average&#95;degree.py to calculate the average hashtag graph degrees. average_degree.py requires two arguments: an input and an output file with path. 

Example usage: `python src/average_degree.py tweet_input/tweets.txt tweet_output/output.txt`

average&#95;degree.py uses only the Python Standard Library (datetime, heapq, json, math, sys, time).
The code has been written and tested in Python 2.7.6 on a Linux 3.13.0-37-generic #64-Ubuntu machine.


## Data Pipeline
[Back to Table of contents](README.md#table-of-contents)

The two main challenges of this task are maintaining the Twitter graph with the sliding window and calculating the vertex degree for each incoming tweet. Both steps need to be effective to ensure fast enough run time and low memory usage for large data sets.

1. To maintain the tweets in the current time window I've used a min heap to store the (time, hashtag list) attributes for each tweet. This data structure allows quick min look up and pop (O(1)), and relatively fast (O(log(n)) insertion. The max time is stored in a separate variable. When a new tweet arrives its time is compared to the max time to check if it's not outside of the window (more than 1 minute earlier). If max time changes the oldest tweets are checked if their time still fall in the new window and are removed as necessary. 
2. To calculate the average vertex degree I've made use of the Handshaking lemma: the sum of all vertex degrees equals to twice the number of edges of a graph. To store the edges I've used a dictionary where the keys are the graph nodes and the values are the list of the other nodes they are connected to. E.g. if  a graph has 3 nodes, which are connected like this: H2-H1-H3 then the resulting dictionary will be {H1:[H2, H3], H2:[H3], H3:[H2]}. Since all edges are accounted for at both nodes when summing the length of each lists we count twice the number of edges (just what the lemma requires). When a new tweet arrives the edges are updated based on the changes of the Tweet heap described above.
 

## Performance
[Back to Table of contents](README.md#table-of-contents)

I've also tested the code with real Twitter streams located in data-gen/tweet_input. Both files contain data rate messages, one of them also has blank lines between 
tweets. 

## Presentation
Presentation for [RadiAction](http://radiaction.site) can be found [here](https://jlantos.github.io/).
