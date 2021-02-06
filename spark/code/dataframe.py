import pyspark
from pyspark.streaming.kafka import KafkaUtils
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.sql import SparkSession
from pyspark.sql.session import SparkSession
from pyspark.conf import SparkConf
import pyspark.sql.types as tp
from pyspark.sql import Row
from pyspark.sql.types import StringType, StructType, StructField
import sys
import json
import os

# ENG
# Spark Application to either create or expand a battle dataframe (.csv) with each row having a string with every pokemon on the opponent side
# (labeled 'pokemon') and the outcome on the other column (labeled 'win').

#ITA
# Applicazione Spark per la creazione o espansione di un dataframe (.csv) contenente una stringa
# che indica i pokemon utilizzati in battaglia e l'esito della stessa.

# START SCRIPT IN bin/ (requires running Zookeeper&KafkaServer, Logstash ed battling bots)
# ./sparkDataframe.sh
#       or
# ./sparkSubmitPython.sh dataframe.py org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.5


brokers="10.100.0.23:9092"
topic = "showdown"

# Create Spark Context
sc = SparkContext(appName="Showdown")
spark = SparkSession(sc)
sc.setLogLevel("WARN")
ssc = StreamingContext(sc, 1)

# DStream for incoming data from Kafka
kvs = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": brokers})

# Schema for a new dataframe
csv_schema = tp.StructType([
    tp.StructField(name = 'pokemon', dataType=tp.StringType(), nullable=True),
    tp.StructField(name = 'win', dataType=tp.FloatType(), nullable=True)
])

# Schema used to load an existing dataframe
schema = tp.StructType([
    tp.StructField(name = '', dataType=tp.LongType(), nullable=True),

    tp.StructField(name = 'pokemon', dataType=tp.StringType(), nullable=True),
    tp.StructField(name = 'win', dataType=tp.FloatType(), nullable=True)
])

# Create an empty dataframe
# pokeDF = spark.createDataFrame(spark.sparkContext.emptyRDD(), schema = csv_schema)

# Load an existing dataframe from the shared volume or from dataset folder
# df = spark.read.csv('../tap/spark/dataset/pokeDF.csv', schema, header=True, sep =',')
# df = spark.read.csv('/shared_data/pokeDF.csv', schema, header=True, sep =',')

try:
    df = spark.read.csv('/shared_data/pokeDF.csv', schema, header=True, sep =',')

pokeDF = df.select('pokemon', 'win')
pokeDF.show()
    
def dataframe_update(key,rdd):
    global pokeDF
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
                json_object["pokemon"][0]["win"]
            ))

    battlestr = battle.collect()
    if not battlestr:
        print("No battle")
        return
    
    print("************")
    print("BATTLESTR: ")
    print(battlestr)


    # create a dataframe with column name 'pokemon' and 'win'
    rowRdd = battle.map(lambda t: Row(pokemon=t[0], win= t[1]))
    
    # create a spark dataframe consisting of one row at a time wich is the added to the existing one
    battleDataFrame =  spark.createDataFrame(rowRdd, schema = csv_schema)
    battleDataFrame.show(truncate = False)
    pokeDF = pokeDF.union(battleDataFrame)
    pokeDF.show()

    # saving/overwriting pokeDF
    pokeDF.toPandas().to_csv(path_or_buf= '/home/pokeDF.csv')
    # writing volume for ML model training
    pokeDF.toPandas().to_csv(path_or_buf= '/shared_data/pokeDF.csv')


# for each RDD received updating dataframe
kvs.foreachRDD(dataframe_update)

ssc.start()
ssc.awaitTermination()


