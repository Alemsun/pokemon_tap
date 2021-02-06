#!/usr/bin/env bash
# Stop
docker stop training

# Remove previuos container 
docker container rm training

docker build ../spark/ --tag training:showdown
docker run -e SPARK_ACTION=training -p 4042:4042 --network poke --name training --volume shared_volume:/shared_data/ -it training:showdown