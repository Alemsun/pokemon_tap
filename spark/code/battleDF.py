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

# Applicazione Spark per la creazione di un file csv contenente una stringa
# che indica i pokemon utilizzati in battaglia e l'esito della stessa

#TO START
# ./sparkSubmitPython.sh battleDF.py org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.5


#EXPAND DATASET

brokers="10.100.0.23:9092"
topic = "showdown"

# Create Spark Context
sc = SparkContext(appName="Showdown")
spark = SparkSession(sc)

sc.setLogLevel("WARN")

ssc = StreamingContext(sc, 1)
kvs = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": brokers})

# battleSchema = tp.StructType([
#     # Todo use proper timestamp
#     tp.StructField(name= 'player', dataType= tp.StringType(),  nullable= True),
#     tp.StructField(name= 'turns',      dataType= tp.LongType(),  nullable= True)
# ])

csv_schema = tp.StructType([
    tp.StructField(name = 'pokemon', dataType=tp.StringType(), nullable=True),
    tp.StructField(name = 'win', dataType=tp.FloatType(), nullable=True)
])

schema = tp.StructType([
    tp.StructField(name = '', dataType=tp.LongType(), nullable=True),

    tp.StructField(name = 'pokemon', dataType=tp.StringType(), nullable=True),
    tp.StructField(name = 'win', dataType=tp.FloatType(), nullable=True)
])

def createDF(rowRdd, schema):
    return spark.createDataFrame(rowRdd, schema=csv_schema)

df = spark.read.csv('../tap/spark/dataset/pokeDF.csv', schema, header=True, sep =',')
pokeDF = df.select('pokemon', 'win')
pokeDF.show()
    
def get_prediction_json(key,rdd):
    global pokeDF
    space = " "
    print ("**********")
    battle = rdd.map(lambda (key, value): json.loads(value)) \
            .map(lambda json_object: (
                json_object["pokemon"][0]["name"] + space +
                json_object["pokemon"][1]["name"] + space +
                json_object["pokemon"][2]["name"] + space +
                json_object["pokemon"][3]["name"] + space +
                json_object["pokemon"][4]["name"] + space +
                json_object["pokemon"][5]["name"],
                json_object["pokemon"][0]["win"]
            ))

    battlestr = battle.collect()
    if not battlestr:
        print("No battle")
        return
    
    print("************")
    print("BATTLESTR: ")
    print(battlestr)


    # create a dataframe with column name 'tweet' and each row will contain the tweet
    rowRdd = battle.map(lambda t: Row(pokemon=t[0], win= t[1]))
    # create a spark dataframe
    

    battleDataFrame =  spark.createDataFrame(rowRdd, schema = csv_schema)
    battleDataFrame.show(truncate = False)
    pokeDF = pokeDF.union(battleDataFrame)
    pokeDF.show()

    # print("Saving DataFrame")
    pokeDF.toPandas().to_csv(path_or_buf= '/home/pokeDF.csv')    
    # print("SAVED")
    
    # new = battleDataFrame.rdd.map(lambda item: {'player': item['player'], 'turns': item['turns']})

    # final_rdd = new.map(json.dumps).map(lambda x: ('key', x))
    # print("FINAL RDD")
    # print(final_rdd.collect())
    
    # final_rdd.saveAsNewAPIHadoopFile(
    # path='-',
    # outputFormatClass="org.elasticsearch.hadoop.mr.EsOutputFormat",
    # keyClass="org.apache.hadoop.io.NullWritable",
    # valueClass="org.elasticsearch.hadoop.mr.LinkedMapWritable",
    # conf=es_conf)



# get the predicted sentiments for the tweets received
kvs.foreachRDD(get_prediction_json)

ssc.start()
ssc.awaitTermination()


