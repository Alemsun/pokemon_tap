#!/usr/bin/env bash
# Stop
docker stop bot1

# Remove previuos container 
docker container rm bot1

# Build
docker build ../docker_sd/ -t bot1:showdown

#Run with environment file
docker run --ip 10.100.0.20 --network poke -p 5000:5000 --name bot1 --env-file ../docker_sd/env_files/bot1.env bot1:showdown
