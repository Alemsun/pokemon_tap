#!/usr/bin/env bash
# Stop
docker stop elasticsearch

# Remove previuos container 
docker container rm elasticsearch

# Build
docker build ../elasticsearch/ --tag showdown:elasticsearch

docker run -t  -p 9200:9200 -p 9300:9300 --ip 10.100.0.51 --name elasticsearch --network poke -e "discovery.type=single-node"  showdown:elasticsearch
