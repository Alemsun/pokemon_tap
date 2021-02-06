import os
import sys
import json
import pyspark
import pyspark.sql.types as tp
from pyspark.streaming.kafka import KafkaUtils
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.sql import SparkSession
from pyspark.sql.session import SparkSession
from pyspark.sql import Row
from pyspark.sql.types import StringType, StructType, StructField
from pyspark.streaming import StreamingContext
from pyspark.conf import SparkConf
from pyspark.streaming import StreamingContext
from pyspark.ml import Pipeline
from pyspark.ml.feature import StopWordsRemover, Word2Vec, RegexTokenizer
from pyspark.ml.classification import LogisticRegression
from sklearn import metrics

# ENG
# Spark application focused on training a Machine Learning pipeline consisting of the following stages:
# - RegexTokenizer: extracting Tokens from the Pokemon string, briefly a list containg a single pokemon for each element
# - Word2Vec: used to create a word embedding from the previously created tokens
# - Logistic Regression: ML model to make binary predictions on the battle outcome based on the composition of the opponent team

# ITA
# Applicazione in Spark che si concentra sul training di una Machine Learning pipeline che consiste dei seguenti stages:
# - RegexTokenizer: estrare un Token per ogni pokemon contenuto nella stringa in input, creando una lista
#                   contenete un pokemon per elemento
# - Word2Vec: utilizzato per creare un word embedding per ogni token in input
# - Logistic Regression: modello di ML utilizzato per effettuare delle predizioni riguardo l'esito della battaglia basandosi sulla
#                   composizione del team avversario

# START SCRIPT IN "bin/" (requires a dataset created with pokeDF.py)
# ./sparkTraining.sh
#       or
# ./sparkSubmitPython.sh training.py org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.5

brokers="10.0.0.23:9093"
topic = "showdown"

# Create Spark Context
sc = SparkContext(appName="Showdown")
spark = SparkSession(sc)
sc.setLogLevel("WARN")

csv_schema = tp.StructType([
    tp.StructField(name = '', dataType=tp.LongType(), nullable=True),

    tp.StructField(name = 'pokemon', dataType=tp.StringType(), nullable=True),
    tp.StructField(name = 'win', dataType=tp.FloatType(), nullable=True)
])

# Loading dataframe from "shared_data/" folder, found in the shared volume between containers
inputDF = spark.read.csv('../tap/spark/dataset/pokeDF.csv', csv_schema, header=True, sep =',')
df = inputDF.persist(pyspark.StorageLevel.MEMORY_AND_DISK)
pokeDF = df.select('pokemon', 'win')
pokeDF.show()

# Randomly splitting originale dataframe in a train set and test set
train_data,test_data = pokeDF.randomSplit(weights = [0.80, 0.20], seed=13) 

print "### TRAIN DATA ###"
train_data.show()
print "### TEST DATA ###" 
test_data.show()

# Creatinge the ML pipeline
stage_1 = RegexTokenizer(inputCol='pokemon', outputCol='tokens', pattern='\\W')
# print("Tokenized")
stage_2 = Word2Vec(inputCol= 'tokens', outputCol='vector')
# print("Vectorized")
model = LogisticRegression(featuresCol='vector', labelCol='win')
# print("Modeled")
pipeline = Pipeline(stages= [stage_1,stage_2,model])

# Training of the created model
pipelineFit = pipeline.fit(train_data) 

unlabeled_data = test_data.select('pokemon') 
print("### UNLABELED DATA ###")
unlabeled_data.show(5)

# Testing on unlabeled data (supervided training) 
predictions = pipelineFit.transform(test_data)
predictions.toPandas().to_csv(path_or_buf= '/home/predictions.csv')    
predictions.show()

# Creating a confusion table and printing an accuracy score based on the correctly labeled data
print("Confusion Table")
predictions.crosstab('win','prediction').show()
actual = predictions.select('win').toPandas()
predicted = predictions.select('prediction').toPandas()
print("No optimization model accuracy: ")
print(metrics.accuracy_score(actual, predicted, normalize=True))

# MODEL OPTIMIZATION (necessary to enhance model accuracy)
# Code available at:  https://spark.apache.org/docs/2.2.0/ml-classification-regression.html#logistic-regression

# Extract the summary from the returned LogisticRegressionModel instance trained
# in the earlier example
trainingSummary = pipelineFit.stages[-1].summary

# Obtain the objective per iteration
objectiveHistory = trainingSummary.objectiveHistory
# print("objectiveHistory:")
# for objective in objectiveHistory:
#     print(objective)

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

# Prediction using the best threshold to predict battle outcome
# train_data,test_data = pokeDF.randomSplit(weights = [0.80, 0.20])
pipelineFit = pipeline.fit(train_data)

predictions = pipelineFit.transform(test_data)
predictions.toPandas().to_csv(path_or_buf= '/home/predictions.csv')    
predictions.show()

print("Confusion Table")
predictions.crosstab('win','prediction').show()
actual = predictions.select('win').toPandas()
predicted = predictions.select('prediction').toPandas()
print("Optimized Accuracy: ")
print(metrics.accuracy_score(actual, predicted, normalize=True))

# Saving the trained model with updated parameters
# pipelineFit.save('/home/opti_model')
# Saving on the shared volume to pass the model to the actual prediction
pipelineFit.write().overwrite().save('/shared_data/opti_model/')