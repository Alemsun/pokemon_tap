import os
import sys
import json
import pyspark
import pyspark.sql.types as tp
from datetime import datetime
from pyspark.streaming.kafka import KafkaUtils
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.sql import SparkSession
from pyspark.sql.session import SparkSession
from pyspark.sql import Row
from pyspark.sql.types import StringType, StructType, StructField
from pyspark.conf import SparkConf
from pyspark.ml import Pipeline
from pyspark.ml.feature import StopWordsRemover, Word2Vec, RegexTokenizer
from pyspark.ml.classification import LogisticRegression
from pyspark.ml import PipelineModel
from elasticsearch import Elasticsearch

# ENG
# Spark application to be considered the heart of the project, running the Data Processing and ML stages taking data with a Direct
# streaming from Kafka and sending the output to Elasticsearch for indexing

# ITA
# Applicazione in Spark che rappresenta il cuore del progetto, svolgendo sia la parte di Data Processing che di ML sui dati provenienti
# da Spark tramite un Direct Approach con Kafka e inviando l'output ad Elasticsearch per l'indexing


# START SCRIPT "bin/" (requires running Zookeper & Kafka Server, Elasticsearch, Logstash and battling bots. Eventually Kibana for Visualization)
# ./sparkShowdown
#       or
# ./sparkSubmitPython.sh showdown_es.py "org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.5,org.elasticsearch:elasticsearch-hadoop:7.7.0"


# Elasticsearch settings
elastic_host="10.100.0.51"
elastic_index="showdown"
elastic_document="_doc"

es_conf = {
# specify the node that we are sending data to (this should be the master)
"es.nodes" : elastic_host,
# specify the port in case it is not the default port
"es.port" : '9200',
# specify a resource in the form 'index/doc-type'
"es.resource" : '%s/%s' % (elastic_index,elastic_document),
# is the input JSON?
"es.input.json" : "yes"
}

mapping = {
    "mappings": {
        "properties": {
            "pokemon": {
                "type": "text"
            },
            "win": {
                "type": "float"
            },
            "prediction":{
                "type": "float"
            },
            "opponet" :{
                "type": "text"
            },
            "turns" : {
                "type": "text"
            },
            "timestamp":{
                "type": "date",
                "format": "yyyy-MM-dd HH:mm:ss"
            },
            "p1":{
                "name":{
                    "type": "text"
                },
                "ability1":{
                    "type": "text"
                },
                "item1":{
                    "type": "text"
                },
                "type1":{
                    "type": "text"
                }
            },
            "p1":{ "name":{ "type": "text"}, "ability1":{ "type": "text"}, "item1":{ "type": "text"}, "type1":{ "type": "text"} },
            "p2":{ "name":{ "type": "text"}, "ability2":{ "type": "text"}, "item2":{ "type": "text"}, "type2":{ "type": "text"} },
            "p3":{ "name":{ "type": "text"}, "ability3":{ "type": "text"}, "item3":{ "type": "text"}, "type3":{ "type": "text"} },
            "p4":{ "name":{ "type": "text"}, "ability4":{ "type": "text"}, "item4":{ "type": "text"}, "type4":{ "type": "text"} },
            "p5":{ "name":{ "type": "text"}, "ability5":{ "type": "text"}, "item5":{ "type": "text"}, "type5":{ "type": "text"} },
            "p6":{ "name":{ "type": "text"}, "ability6":{ "type": "text"}, "item6":{ "type": "text"}, "type6":{ "type": "text"} }
        }
    }
}
elastic = Elasticsearch(hosts=[elastic_host])


# make an API call to the Elasticsearch cluster
# and have it return a response:
response = elastic.indices.create(
    index=elastic_index,
    body=mapping,
    ignore=400 # ignore 400 already exists code
)

if 'acknowledged' in response:
    if response['acknowledged'] == True:
        print ("INDEX MAPPING SUCCESS FOR INDEX:", response['index'])

# catch API error response
elif 'error' in response:
    print ("ERROR:", response['error']['root_cause'])
    print ("TYPE:", response['error']['type'])

conf = SparkConf(loadDefaults=False)
conf.set("es.index.auto.create", "true")

brokers="10.100.0.23:9092"
topic = "showdown"

# Create Spark Context
sc = SparkContext(appName="Showdown")
spark = SparkSession(sc)
sc.setLogLevel("WARN")
ssc = StreamingContext(sc, 1)

# Catching Kafka Stream
kvs = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": brokers})

battleSchema = tp.StructType([
    tp.StructField(name = 'pokemon', dataType=tp.StringType(), nullable=True),
    tp.StructField(name = 'win', dataType=tp.FloatType(), nullable=True),
    tp.StructField(name = 'opponent', dataType=tp.StringType(), nullable=True),
    tp.StructField(name = 'turns', dataType=tp.LongType(), nullable = True),
    tp.StructField(name = 'timestamp', dataType=StringType(), nullable = True),
    # p1
    tp.StructField(name = "p1", dataType=tp.StringType(), nullable=True), tp.StructField(name = "ability1", dataType=tp.StringType(), nullable=True), tp.StructField(name = "item1", dataType=tp.StringType(), nullable=True), tp.StructField(name = "type1", dataType=tp.StringType(), nullable=True),
    # p2
    tp.StructField(name = "p2", dataType=tp.StringType(), nullable=True), tp.StructField(name = "ability2", dataType=tp.StringType(), nullable=True), tp.StructField(name = "item2", dataType=tp.StringType(), nullable=True), tp.StructField(name = "type2", dataType=tp.StringType(), nullable=True),
    # p3
    tp.StructField(name = "p3", dataType=tp.StringType(), nullable=True), tp.StructField(name = "ability3", dataType=tp.StringType(), nullable=True), tp.StructField(name = "item3", dataType=tp.StringType(), nullable=True), tp.StructField(name = "type3", dataType=tp.StringType(), nullable=True),
    # p4
    tp.StructField(name = "p4", dataType=tp.StringType(), nullable=True), tp.StructField(name = "ability4", dataType=tp.StringType(), nullable=True), tp.StructField(name = "item4", dataType=tp.StringType(), nullable=True), tp.StructField(name = "type4", dataType=tp.StringType(), nullable=True),
    # p5
    tp.StructField(name = "p5", dataType=tp.StringType(), nullable=True), tp.StructField(name = "ability5", dataType=tp.StringType(), nullable=True), tp.StructField(name = "item5", dataType=tp.StringType(), nullable=True), tp.StructField(name = "type5", dataType=tp.StringType(), nullable=True),
    # p6
    tp.StructField(name = "p6", dataType=tp.StringType(), nullable=True), tp.StructField(name = "ability6", dataType=tp.StringType(), nullable=True), tp.StructField(name = "item6", dataType=tp.StringType(), nullable=True), tp.StructField(name = "type6", dataType=tp.StringType(), nullable=True),
])

# pipelineFit = PipelineModel.load('/opt/tap/spark/model/')
pipelineFit = PipelineModel.load('/shared_data/opti_model/')

def get_prediction_json(key,rdd):
    space = " "
    print ("**********")
    # extracting specific data from each event
    battle = rdd.map(lambda (key, value): json.loads(value)) \
            .map(lambda json_object: (
                json_object["pokemon"][0]["name"] + space +
                json_object["pokemon"][1]["name"] + space +
                json_object["pokemon"][2]["name"] + space +
                json_object["pokemon"][3]["name"] + space +
                json_object["pokemon"][4]["name"] + space +
                json_object["pokemon"][5]["name"],
                json_object["pokemon"][0]["win"],
                # p1
                json_object["pokemon"][0]["name"], json_object["pokemon"][0]["ability"],json_object["pokemon"][0]["item"], json_object["pokemon"][0]["types"][0],
                # p2
                json_object["pokemon"][1]["name"], json_object["pokemon"][1]["ability"],json_object["pokemon"][1]["item"], json_object["pokemon"][1]["types"][0],
                # p3
                json_object["pokemon"][2]["name"], json_object["pokemon"][2]["ability"],json_object["pokemon"][2]["item"], json_object["pokemon"][2]["types"][0],
                # p4
                json_object["pokemon"][3]["name"], json_object["pokemon"][3]["ability"],json_object["pokemon"][3]["item"], json_object["pokemon"][3]["types"][0],
                # p5
                json_object["pokemon"][4]["name"], json_object["pokemon"][4]["ability"],json_object["pokemon"][4]["item"], json_object["pokemon"][4]["types"][0],
                # p6
                json_object["pokemon"][5]["name"], json_object["pokemon"][5]["ability"],json_object["pokemon"][5]["item"], json_object["pokemon"][5]["types"][0],

                json_object["battle"][0]["player"],
                json_object["battle"][0]["turns"]
            ))
    battlestr = battle.collect()
    if not battlestr:
        print("No battle")
        return
    
    print("************")
    print("BATTLESTR: ")
    print(battlestr)

    # create a dataframe with all different data collected
    rowRdd = battle.map(lambda t: Row(pokemon=t[0], win= t[1],
                                p1=t[2], ability1=t[3], item1=t[4], type1=t[5],
                                p2=t[6], ability2=t[7], item2=t[8], type2=t[9],
                                p3=t[10], ability3=t[11], item3=t[12], type3=t[13],
                                p4=t[14], ability4=t[15], item4=t[16], type4=t[17],
                                p5=t[18], ability5=t[19], item5=t[20], type5=t[21],
                                p6=t[22], ability6=t[23], item6=t[24], type6=t[25],
                                opponent=t[26], turns=t[27], timestamp= datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                                ))
    # create a spark dataframe
    battleDataFrame =  spark.createDataFrame(rowRdd, schema = battleSchema)
    battleDataFrame.show()
    # transform the data using the pipeline and get the predicted sentiment
    data = pipelineFit.transform(battleDataFrame)
    #add timestamp
    # data.withColumn("timestamp", current_timestamp().cast("string"))
    data.show()

    new = data.rdd.map(lambda item: {'pokemon': item['pokemon'], 'win': item['win'], 'prediction':item['prediction'], 
                                    'p1':item['p1'], 'ability1':item['ability1'], 'item1':item['item1'], 'type1':item['type1'],
                                    'p2':item['p2'], 'ability2':item['ability2'], 'item2':item['item2'], 'type2':item['type2'],
                                    'p3':item['p3'], 'ability3':item['ability3'], 'item3':item['item3'], 'type3':item['type3'],
                                    'p4':item['p4'], 'ability4':item['ability4'], 'item4':item['item4'], 'type4':item['type4'],
                                    'p5':item['p5'], 'ability5':item['ability5'], 'item5':item['item5'], 'type5':item['type5'],
                                    'p6':item['p6'], 'ability6':item['ability6'], 'item6':item['item6'], 'type6':item['type6'],
                                    'opponent':item['opponent'], 'turns':item['turns'], 'timestamp':item['timestamp']})

    final_rdd = new.map(json.dumps).map(lambda x: ('key', x))
    print("FINAL RDD")
    print(final_rdd.collect())
    
    #Sending to Elastic
    final_rdd.saveAsNewAPIHadoopFile(
    path='-',
    outputFormatClass="org.elasticsearch.hadoop.mr.EsOutputFormat",
    keyClass="org.apache.hadoop.io.NullWritable",
    valueClass="org.elasticsearch.hadoop.mr.LinkedMapWritable",
    conf=es_conf)

# get the predicted sentiments for the data received
kvs.foreachRDD(get_prediction_json)

ssc.start()
ssc.awaitTermination()