FROM docker.elastic.co/logstash/logstash:7.10.1

RUN rm -f /usr/share/logstash/pipeline/logstash.conf

ADD config/logstash.yml /usr/share/logstash/config/logstash.yml
ADD config/pylog.conf /usr/share/logstash/pipeline/pylog.conf