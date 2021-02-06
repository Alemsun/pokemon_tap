#!/usr/bin/env bash
# Stop
docker stop bot2
docker stop bot3
docker stop bot4
docker stop bot5
docker stop bot6
docker stop bot7
docker stop bot8
docker stop bot9

# Remove previuos container 
docker container rm bot2
docker container rm bot3
docker container rm bot4
docker container rm bot5
docker container rm bot6
docker container rm bot7
docker container rm bot8
docker container rm bot9

# Build
docker build ../docker_sd/ -t bot2:showdown
docker build ../docker_sd/ -t bot3:showdown
docker build ../docker_sd/ -t bot4:showdown
docker build ../docker_sd/ -t bot5:showdown
docker build ../docker_sd/ -t bot6:showdown
docker build ../docker_sd/ -t bot7:showdown
docker build ../docker_sd/ -t bot8:showdown
docker build ../docker_sd/ -t bot9:showdown

#Run with environment file
docker run --ip 10.100.0.19 -d --network project_poke --name bot2 --env-file ../docker_sd/env_files/bot2.env bot2:showdown
docker run --ip 10.100.0.18 -d --network project_poke --name bot3 --env-file ../docker_sd/env_files/bot3.env bot3:showdown
docker run --ip 10.100.0.17 -d --network project_poke --name bot4 --env-file ../docker_sd/env_files/bot4.env bot4:showdown
docker run --ip 10.100.0.16 -d --network project_poke --name bot5 --env-file ../docker_sd/env_files/bot5.env bot5:showdown
docker run --ip 10.100.0.15 -d --network project_poke --name bot6 --env-file ../docker_sd/env_files/bot6.env bot6:showdown
docker run --ip 10.100.0.14 -d --network project_poke --name bot7 --env-file ../docker_sd/env_files/bot7.env bot7:showdown
docker run --ip 10.100.0.13 -d --network project_poke --name bot8 --env-file ../docker_sd/env_files/bot8.env bot8:showdown
docker run --ip 10.100.0.12    --network project_poke --name bot9 --env-file ../docker_sd/env_files/bot9.env bot9:showdown

