from pyspark.streaming.kafka import KafkaUtils
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.sql import SparkSession
from pyspark.sql import Row
from pyspark.sql.types import StringType, StructType, StructField

import sys
import json
from pyspark import SparkContext
from pyspark.sql.session import SparkSession
from pyspark.streaming import StreamingContext
import pyspark
from pyspark.conf import SparkConf
from pyspark.streaming import StreamingContext
import pyspark.sql.types as tp
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, OneHotEncoderEstimator, VectorAssembler
from pyspark.ml.feature import StopWordsRemover, Word2Vec, RegexTokenizer
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.feature import HashingTF, IDF, Tokenizer
from pyspark.ml.classification import NaiveBayes
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
import os
import sys

from pyspark.ml import PipelineModel

from elasticsearch import Elasticsearch

import uuid
# MOST IMPORTANT
# SENDS DATA TO ELASTISC_SEARCH
#TO START
# ./sparkSubmitPython.sh showdown_es.py "org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.5,org.elasticsearch:elasticsearch-hadoop:7.7.0"

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
            }
        }
    }
}

from elasticsearch import Elasticsearch
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

# Elastic Search
conf = SparkConf(loadDefaults=False)
conf.set("es.index.auto.create", "true")

brokers="10.100.0.23:9092"
topic = "showdown"

# Create Spark Context
sc = SparkContext(appName="Showdown")
spark = SparkSession(sc)

sc.setLogLevel("WARN")

ssc = StreamingContext(sc, 1)
kvs = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": brokers})

battleSchema = tp.StructType([
    # tp.StructField(name = '', dataType=tp.LongType(), nullable=True),

    tp.StructField(name = 'pokemon', dataType=tp.StringType(), nullable=True),
    tp.StructField(name = 'win', dataType=tp.FloatType(), nullable=True),
    tp.StructField(name = "p1", dataType=tp.StringType(), nullable=True),
    tp.StructField(name = "ability1", dataType=tp.StringType(), nullable=True),
    tp.StructField(name = "item1", dataType=tp.StringType(), nullable=True),
    tp.StructField(name = "type1", dataType=tp.StringType(), nullable=True),
    # tp.StructField(name = "s_type1", dataType=tp.StringType(), nullable=True)
])

pipelineFit = PipelineModel.load('/opt/tap/spark/model/')

def get_prediction_json(key,rdd):
    space = " "
    print ("**********")
    # battle = rdd.map(lambda (key, value): json.loads(value)) \
    #         .map(lambda json_object: (
    #             json_object["battle"][0]["player"],
    #             json_object["battle"][0]["turns"],
    #             # json_object["pokemon"]
    #         ))
    battle = rdd.map(lambda (key, value): json.loads(value)) \
            .map(lambda json_object: (
                json_object["pokemon"][0]["name"] + space +
                json_object["pokemon"][1]["name"] + space +
                json_object["pokemon"][2]["name"] + space +
                json_object["pokemon"][3]["name"] + space +
                json_object["pokemon"][4]["name"] + space +
                json_object["pokemon"][5]["name"],
                json_object["pokemon"][0]["win"],
                json_object["pokemon"][0]["name"], json_object["pokemon"][0]["ability"],json_object["pokemon"][0]["item"], json_object["pokemon"][0]["types"][0]
            ))
    battlestr = battle.collect()
    if not battlestr:
        print("No battle")
        return
    
    print("************")
    print("BATTLESTR: ")
    print(battlestr)

    # create a dataframe with column name 'tweet' and each row will contain the tweet
    rowRdd = battle.map(lambda t: Row(pokemon=t[0], win= t[1], p1=t[2], ability1=t[3], item1=t[4], type1=t[5]))
    # create a spark dataframe
    battleDataFrame =  spark.createDataFrame(rowRdd, schema = battleSchema)
    battleDataFrame.show()
    # transform the data using the pipeline and get the predicted sentiment
    data = pipelineFit.transform(battleDataFrame)
    data.show()

    new = data.rdd.map(lambda item: {'pokemon': item['pokemon'], 'win': item['win'], 'prediction':item['prediction'], 'p1':item['p1'], 'ability1':item['ability1'], 'item1':item['item1'], 'type1':item['type1']})

    final_rdd = new.map(json.dumps).map(lambda x: ('key', x))
    print("FINAL RDD")
    print(final_rdd.collect())
    
    final_rdd.saveAsNewAPIHadoopFile(
    path='-',
    outputFormatClass="org.elasticsearch.hadoop.mr.EsOutputFormat",
    keyClass="org.apache.hadoop.io.NullWritable",
    valueClass="org.elasticsearch.hadoop.mr.LinkedMapWritable",
    conf=es_conf)



# get the predicted sentiments for the tweets received
kvs.foreachRDD(get_prediction_json)

ssc.start()
ssc.awaitTermination()