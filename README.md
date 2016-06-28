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

![Alt text](app/static/img/room_graph.png?raw=true "Room map")


## AWS Clusters
[Back to Table of contents](README.md#table-of-contents)

[RadiAction](http://radiaction.site) runs on four clusters on AWS:
<ul>
<li>4 m3.large nodes for Kafka and Spark streaming</li>
<li>3 m3.large nodes for Cassandra </li>
<li>1 m3.large Neo4j</li>
<li>1 m3.large nodes for Flask and the Kafka Producer Pythons cript</li>
</ul>
As of July, 2016, this system costs ~$? a day with AWS on-demand instances used.

## Data Pipeline
[Back to Table of contents](README.md#table-of-contents)

![Alt text](app/static/img/pipeline.png?raw=true "Pipeline")

### Data source
 

## Performance
[Back to Table of contents](README.md#table-of-contents)

I've also tested the code with real Twitter streams located in data-gen/tweet_input. Both files contain data rate messages, one of them also has blank lines between 
tweets. 

## Presentation
Presentation for [RadiAction](http://radiaction.site) can be found [here](https://jlantos.github.io/).
