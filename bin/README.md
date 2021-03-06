# Scripts

Before running the scripts, assure yourself that the scripts execution mode is not compromised by the download.

---
- ```./botArmy(Compose).sh```:    8 additional bots to quicken data collection ( add Compose to execute the bots on the docker-compose network).
- ```./elasticsearch.sh```:       run Elasticsearch service.
- ```./kafkaStartServer.sh```: run Kafka Server, needs data from Logstash to create "Showdown Topic" (requires Zookeeper).
- ```./kafkaStartZk.sh```: run Zookeeper Server.
- ```./kibana.sh```: run Kibana, used as an ElasticSearch UI, open *localhost:5601* on a Web Browser to connect.
- ```./logstash.sh```: run Logstash to send battle events to Kafka (requires showdownBot, Zookeeper and Kafka).
- ```./network.sh```: create a Docker Network (external to the docker-compose one).
- ```./showdownBot.sh```: run a single battle bot.
- ```./sparkSubmitPython.sh```: script to run some pyspark code (requires .py file directory (spark/code/), *maven repository file* matching artifact:kafka_version:spark_version and running Kafka with an existing topic). 
- ```./spark[Showdown][Dataframe][Training].sh```: scripts tailored respectively on the project to run main spark service, spark dataframe and machine learning model training (see the requirements above).   
