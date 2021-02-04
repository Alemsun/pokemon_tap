#!/usr/bin/env bash
# Stop
docker stop kafkaZK

# Remove previuos container 
docker container rm kafkaZK

docker build ../kafka/ --tag showdown:kafka
docker run -e KAFKA_ACTION=start-zk --network poke --ip 10.100.0.22  -p 2181:2181 --name kafkaZK -it showdown:kafka