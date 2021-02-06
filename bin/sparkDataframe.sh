#!/usr/bin/env bash
# Stop
docker stop dataframe

# Remove previuos container 
docker container rm dataframe

docker build ../spark/ --tag dataframe:showdown
docker run -e SPARK_ACTION=dataframe -p 4041:4041 --network poke --name dataframe --volume shared_volume:/shared_data -it dataframe:showdown