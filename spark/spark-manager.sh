#!/bin/bash
[[ -z "${SPARK_ACTION}" ]] && { echo "SPARK_ACTION required"; exit 1; }

# ACTIONS start-zk, start-kafka, create-topic, 

echo "Running action ${SPARK_ACTION}"
case ${SPARK_ACTION} in
"example")
echo "Running example ARGS $@"
./bin/run-example $@
;;
"spark-shell")
./bin/spark-shell --master local[2]
;;
"pyspark")
./bin/pyspark --master local[2]
;;
"spark-submit-python")
#  ./bin/spark-submit --packages $2 /opt/tap/$1
./bin/spark-submit --packages "org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.5,org.elasticsearch:elasticsearch-hadoop:7.7.0" /opt/tap/full_data_test.py
;;
"spark-submit-apps")
 ./bin/spark-submit --packages $3 --class $1 /opt/tap/apps/$2
;;
"pytap")
cd /opt/tap/
python ${TAP_CODE}
;;
"bash")
while true
do
	echo "Keep Alive"
	sleep 10
done
;;
esac

