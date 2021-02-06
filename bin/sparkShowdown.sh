#!/usr/bin/env bash
# Stop
docker stop showdown

# Remove previuos container 
docker container rm showdown

docker build ../spark/ --tag showdown:spark
docker run -e SPARK_ACTION=showdown -p 4040:4040 --network poke --volume shared_volume:/shared_data/ --name showdown -it showdown:spark