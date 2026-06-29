FROM python:3.11-slim

# Install Java (required by Spark)
RUN apt-get update && \
    apt-get install -y default-jre wget && \
    apt-get clean;

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the necessary JAR files to a local lib directory
RUN mkdir -p /jars
RUN wget -qO /jars/spark-sql-kafka-0-10_2.12-3.5.1.jar https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.5.1/spark-sql-kafka-0-10_2.12-3.5.1.jar
RUN wget -qO /jars/kafka-clients-3.4.1.jar https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.4.1/kafka-clients-3.4.1.jar
RUN wget -qO /jars/commons-pool2-2.11.1.jar https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar
RUN wget -qO /jars/spark-token-provider-kafka-0-10_2.12-3.5.1.jar https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.5.1/spark-token-provider-kafka-0-10_2.12-3.5.1.jar
RUN wget -qO /jars/postgresql-42.7.3.jar https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.3/postgresql-42.7.3.jar

# Explicitly copy only the exact files our Spark job requires
COPY postgres_utils.py .
COPY streaming_job.py .

# Run spark-submit, pointing to our local JARs
CMD ["spark-submit", \
     "--jars", "/jars/spark-sql-kafka-0-10_2.12-3.5.1.jar,/jars/kafka-clients-3.4.1.jar,/jars/commons-pool2-2.11.1.jar,/jars/spark-token-provider-kafka-0-10_2.12-3.5.1.jar,/jars/postgresql-42.7.3.jar", \
     "streaming_job.py"]