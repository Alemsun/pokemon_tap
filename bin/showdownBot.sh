#!/usr/bin/env bash
# Stop
docker stop tap2021

# Remove previuos container 
docker container rm tap2021

# Build
docker build ../docker_sd/ -t tap2021:showdown

#Run with environment file
docker run --ip 10.100.0.20 --network poke -p 5000:5000 --env-file ../docker_sd/tap2021.env tap2021:showdown
