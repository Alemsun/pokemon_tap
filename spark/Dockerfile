FROM openjdk:8-jre

ENV PATH $SPARK_DIR/bin:$PATH
ENV SPARK_VERSION=2.4.5
ENV SPARK_DIR=/opt/spark
ENV PATH $SPARK_DIR/bin:$PATH

# ADD setup/spark-${SPARK_VERSION}-bin-hadoop2.7.tgz /opt
RUN apt-get update && apt-get -y install bash python python-pip netcat python-pandas libatlas3-base libopenblas-base wget
RUN wget -O spark-${SPARK_VERSION}-bin-hadoop2.7.tgz https://archive.apache.org/dist/spark/spark-2.4.5/spark-2.4.5-bin-hadoop2.7.tgz \
    && tar -xvzf spark-${SPARK_VERSION}-bin-hadoop2.7.tgz \
    && mv spark-${SPARK_VERSION}-bin-hadoop2.7 /opt

RUN pip install pyspark numpy elasticsearch scikit-learn scipy matplotlib
# Create Sym Link 
RUN ln -s /opt/spark-${SPARK_VERSION}-bin-hadoop2.7 ${SPARK_DIR} 

# Add Dataset Folder
ADD dataset /opt/tap/spark/dataset
# Add Model Folder
ADD model /opt/tap/spark/model
# Add Python Code
ADD code/*  /opt/tap/
# Add Spark Manager
ADD spark-manager.sh $SPARK_DIR/bin/spark-manager

WORKDIR ${SPARK_DIR}
ENTRYPOINT [ "spark-manager" ]