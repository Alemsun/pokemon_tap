# TAP x Pokemon
Data pipeline from Pokemon Showdown to Kibana for a University Project.

# Description
The Data Pipeline components are:

- **docker_sd**: executing one or multiple bots made by pmriglia (https://github.com/pmariglia/showdown).
- **logstash**: used to *ingest* data coming from the bots and send data to the showdown kafka topic.
- **Kafka**: event *streaming* platform, connects logstash to the Spark processing component.
- **Spark**: defined as a unified analitycs engine, here it has the job to *process* the incoming data stream, make *predictions* about battle results using the specific **MLlib** library and send all the above to Elasticsearch.
- **Elasticsearch**: Indexing incoming data.
- **Kibana**: UI dedicated to Data Visualization.
