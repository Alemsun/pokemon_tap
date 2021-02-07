#!/bin/bash
[[ -z "${SPARK_ACTION}" ]] && { echo "SPARK_ACTION required"; exit 1; }

# ACTIONS start-zk, start-kafka, create-topic, 

echo "Running action ${SPARK_ACTION}"
case ${SPARK_ACTION} in

"spark-submit-python")
./bin/spark-submit --packages $2 /opt/tap/$1
;;
"showdown")
#  ./bin/spark-submit --packages $2 /opt/tap/$1
./bin/spark-submit --packages "org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.5,org.elasticsearch:elasticsearch-hadoop:7.7.0" /opt/tap/showdown_es.py
;;
"dataframe")
#  ./bin/spark-submit --packages $2 /opt/tap/$1
./bin/spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.5 /opt/tap/dataframe.py
;;
"training")
#  ./bin/spark-submit --packages $2 /opt/tap/$1
./bin/spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.5 /opt/tap/training.py
;;

"bash")
while true
do
	echo "Keep Alive"
	sleep 10
done
;;
esac

