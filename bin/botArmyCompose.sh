#!/usr/bin/env bash
# Stop
docker stop bot2_compose
docker stop bot3_compose
docker stop bot4_compose
docker stop bot5_compose
docker stop bot6_compose
docker stop bot7_compose
docker stop bot8_compose
docker stop bot9_compose



# Remove previuos container 
docker container rm bot2_compose
docker container rm bot3_compose
docker container rm bot4_compose
docker container rm bot5_compose
docker container rm bot6_compose
docker container rm bot7_compose
docker container rm bot8_compose
docker container rm bot9_compose

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
docker run --ip 10.100.0.19 -d --network project_poke --name bot2_compose --env-file ../docker_sd/env_files/bot2.env bot2:showdown
docker run --ip 10.100.0.18 -d --network project_poke --name bot3_compose --env-file ../docker_sd/env_files/bot3.env bot3:showdown
docker run --ip 10.100.0.17 -d --network project_poke --name bot4_compose --env-file ../docker_sd/env_files/bot4.env bot4:showdown
docker run --ip 10.100.0.16 -d --network project_poke --name bot5_compose --env-file ../docker_sd/env_files/bot5.env bot5:showdown
docker run --ip 10.100.0.15 -d --network project_poke --name bot6_compose --env-file ../docker_sd/env_files/bot6.env bot6:showdown
docker run --ip 10.100.0.14 -d --network project_poke --name bot7_compose --env-file ../docker_sd/env_files/bot7.env bot7:showdown
docker run --ip 10.100.0.13 -d --network project_poke --name bot8_compose --env-file ../docker_sd/env_files/bot8.env bot8:showdown
docker run --ip 10.100.0.12    --network project_poke --name bot9_compose --env-file ../docker_sd/env_files/bot9.env bot9:showdown

