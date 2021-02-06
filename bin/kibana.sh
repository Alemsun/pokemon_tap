#!/usr/bin/env bash
# Stop
docker stop kibana

#  Remove previuos container 
docker container rm kibana

# Build
docker build ../kibana/ --tag showdown:kibana

docker stop kibana
docker run -p 5601:5601 --ip 10.100.0.52 --network poke --name kibana showdown:kibana
