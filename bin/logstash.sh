#!/usr/bin/env bash
# Stop
docker stop logstash

# Remove previuos container 
docker container rm logstash

# Build
docker build ../logstash/ -t logstash:showdown

#Run with environment file
docker run --ip 10.100.0.30 --network poke --name logstash logstash:showdown
