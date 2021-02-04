#!/usr/bin/env bash
# Stop
docker stop kafkaServer

# Remove previuos container 
docker container rm kafkaServer

docker build ../kafka/ --tag showdown:kafka
docker stop kafkaServer
docker run -e KAFKA_ACTION=start-kafka --network poke --ip 10.100.0.23  -p 9092:9092 -p 9093:9093 --name kafkaServer -it showdown:kafka