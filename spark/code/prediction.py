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
from pyspark.ml.regression import LinearRegression 
import os
import sys

from sklearn import metrics

from elasticsearch import Elasticsearch

import uuid

# Applicazione Spark per la creazione di un file csv contenente una stringa
# che indica i pokemon utilizzati in battaglia e l'esito della stessa

#TO START
# ./sparkSubmitPython.sh battleDF.py org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.5


# elastic_host="10.0.0.51"
# elastic_index="showdown"
# elastic_document="_doc"

# es_conf = {
# # specify the node that we are sending data to (this should be the master)
# "es.nodes" : elastic_host,
# # specify the port in case it is not the default port
# "es.port" : '9200',
# # specify a resource in the form 'index/doc-type'
# "es.resource" : '%s/%s' % (elastic_index,elastic_document),
# # is the input JSON?
# "es.input.json" : "yes"
# }

# mapping = {
#     "mappings": {
#         "properties": {
#             "player": {
#                 "type": "text"
#             },
#             "turns": {
#                 "type": "integer"
#             }
#         }
#     }
# }

# from elasticsearch import Elasticsearch
# elastic = Elasticsearch(hosts=[elastic_host])

# make an API call to the Elasticsearch cluster
# and have it return a response:
# response = elastic.indices.create(
#     index=elastic_index,
#     body=mapping,
#     ignore=400 # ignore 400 already exists code
# )

# if 'acknowledged' in response:
#     if response['acknowledged'] == True:
#         print ("INDEX MAPPING SUCCESS FOR INDEX:", response['index'])

# # catch API error response
# elif 'error' in response:
#     print ("ERROR:", response['error']['root_cause'])
#     print ("TYPE:", response['error']['type'])

# Elastic Search
# conf = SparkConf(loadDefaults=False)
# conf.set("es.index.auto.create", "true")

brokers="10.0.0.23:9093"
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
    tp.StructField(name = '', dataType=tp.LongType(), nullable=True),

    tp.StructField(name = 'pokemon', dataType=tp.StringType(), nullable=True),
    tp.StructField(name = 'win', dataType=tp.FloatType(), nullable=True)
])

def createDF(rowRdd, schema):
    return spark.createDataFrame(rowRdd, schema=csv_schema)

inputDF = spark.read.csv('../tap/spark/dataset/pokeDF.csv', csv_schema, header=True, sep =',')
df = inputDF.persist(pyspark.StorageLevel.MEMORY_AND_DISK)
pokeDF = df.select('pokemon', 'win')
pokeDF.show()

train_data,test_data = pokeDF.randomSplit(weights = [0.80, 0.20], seed = 13) 

print "###TRAIN DATA###"
train_data.show()
print "###TEST DATA###" 
test_data.show()

stage_1 = RegexTokenizer(inputCol='pokemon', outputCol='tokens', pattern='\\W')
print("Tokenized")
stage_2 = Word2Vec(inputCol= 'tokens', outputCol='vector')
print("Vectorized")
model = LogisticRegression(featuresCol='vector', labelCol='win')
print("Modeled")
pipeline = Pipeline(stages= [stage_1,stage_2,model])

pipelineFit = pipeline.fit(train_data)
print("Trained")

# results = pipelineFit.evaluate(train_data)
# print 'Rsquared Error :', results.r2 

unlabeled_data = test_data.select('pokemon') 
print("###UNLABELED DATA###")
unlabeled_data.show(5)

predictions = pipelineFit.transform(test_data)
predictions.toPandas().to_csv(path_or_buf= '/home/predictions.csv')    
predictions.show()

########################
# Extract the summary from the returned LogisticRegressionModel instance trained
# in the earlier example
trainingSummary = pipelineFit.stages[-1].summary

# Obtain the objective per iteration
objectiveHistory = trainingSummary.objectiveHistory
print("objectiveHistory:")
for objective in objectiveHistory:
    print(objective)

# Obtain the receiver-operating characteristic as a dataframe and areaUnderROC.
trainingSummary.roc.show()
print("areaUnderROC: " + str(trainingSummary.areaUnderROC))

# Set the model threshold to maximize F-Measure
fMeasure = trainingSummary.fMeasureByThreshold
maxFMeasure = fMeasure.groupBy().max('F-Measure').select('max(F-Measure)').head()
bestThreshold = fMeasure.where(fMeasure['F-Measure'] == maxFMeasure['max(F-Measure)']) \
    .select('threshold').head()['threshold']
model.setThreshold(bestThreshold)
#######################
predictions.crosstab('win','prediction').show()

actual = predictions.select('win').toPandas()
predicted = predictions.select('prediction').toPandas()

print(metrics.accuracy_score(actual, predicted, normalize=True))

#### BEST THRESHOLD ###

pipelineFit = pipeline.fit(train_data)

predictions = pipelineFit.transform(test_data)
predictions.toPandas().to_csv(path_or_buf= '/home/predictions.csv')    
predictions.show()

predictions.crosstab('win','prediction').show()

actual = predictions.select('win').toPandas()
predicted = predictions.select('prediction').toPandas()

print(metrics.accuracy_score(actual, predicted, normalize=True))

pipelineFit.save('/home/opti_model')

# modelSummary = pipelineFit.stages[-1].summary
# modelSummary.accuracy

# pokeDF = spark.createDataFrame(spark.sparkContext.emptyRDD(), schema = csv_schema)

# def get_prediction_json(key,rdd):
#     global pokeDF
#     space = " "
#     print ("**********")
#     battle = rdd.map(lambda (key, value): json.loads(value)) \
#             .map(lambda json_object: (
#                 json_object["pokemon"][0]["name"] + space +
#                 json_object["pokemon"][1]["name"] + space +
#                 json_object["pokemon"][2]["name"] + space +
#                 json_object["pokemon"][3]["name"] + space +
#                 json_object["pokemon"][4]["name"] + space +
#                 json_object["pokemon"][5]["name"],
#                 json_object["pokemon"][0]["win"]
#             ))

#     battlestr = battle.collect()
#     if not battlestr:
#         print("No battle")
#         return
    
#     print("************")
#     print("BATTLESTR: ")
#     print(battlestr)


#     # create a dataframe with column name 'tweet' and each row will contain the tweet
#     rowRdd = battle.map(lambda t: Row(pokemon=t[0], win= t[1]))
#     # create a spark dataframe
    

#     battleDataFrame =  spark.createDataFrame(rowRdd, schema = csv_schema)
#     battleDataFrame.show(truncate = False)
#     pokeDF = pokeDF.union(battleDataFrame)
#     pokeDF.show()

#     # print("Saving DataFrame")
#     pokeDF.toPandas().to_csv(path_or_buf= '/home/pokeDF.csv')    
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
# kvs.foreachRDD(get_prediction_json)

# ssc.start()
# ssc.awaitTermination()


