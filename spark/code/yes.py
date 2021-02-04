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

from elasticsearch import Elasticsearch

import uuid

reload(sys)
# Set encoding to UTF
sys.setdefaultencoding('utf-8')


elastic_host="10.0.0.51"
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
            "player": {
                "type": "text"
            },
            "turns": {
                "type": "integer"
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

brokers="10.0.0.23:9093"
topic = "showdown"

# Create Spark Context
sc = SparkContext(appName="Showdown")
spark = SparkSession(sc)

sc.setLogLevel("WARN")

ssc = StreamingContext(sc, 1)
kvs = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": brokers})


battleSchema = tp.StructType([
    # Todo use proper timestamp
    tp.StructField(name= 'player', dataType= tp.StringType(),  nullable= True),
    tp.StructField(name= 'turns',      dataType= tp.LongType(),  nullable= True)
])

def get_prediction_json(key,rdd):
    print ("**********")
    battle = rdd.map(lambda (key, value): json.loads(value)) \
            .map(lambda json_object: (
                json_object["battle"][0]["player"],
                long(json_object["battle"][0]["turns"])
            ))
    battlestr = battle.collect()
    if not battlestr:
        print("No battle")
        return
    
    print("************")
    print("BATTLESTR: ")
    print(battlestr)

    # create a dataframe with column name 'tweet' and each row will contain the tweet
    rowRdd = battle.map(lambda t: Row(player=t[0], turns= t[1]))
    # create a spark dataframe
    battleDataFrame =  spark.createDataFrame(rowRdd, schema = battleSchema)
    battleDataFrame.show(truncate = False)
    # transform the data using the pipeline and get the predicted sentiment

    new = battleDataFrame.rdd.map(lambda item: {"player": item["player"], "turns": item["turns"]})

    final_rdd = new.map(lambda x: json.dumps(x, default=str)).map(lambda x: ('key', x))
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