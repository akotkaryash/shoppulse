from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, LongType
from postgres_utils import upsert_batch

print("Initializing PySpark Session...")
spark = SparkSession.builder \
    .appName("ShopPulse_Streaming_Ingestion") \
    .config("spark.sql.shuffle.partitions", "2") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

event_schema = StructType([
    StructField("event_id", StringType(), True),
    StructField("user_key", IntegerType(), True),
    StructField("product_key", IntegerType(), True),
    StructField("event_type", StringType(), True),
    StructField("quantity", IntegerType(), True),
    StructField("amount", DoubleType(), True),
    StructField("event_ts", LongType(), True)
])

print("Connecting to Kafka topic 'events'...")
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:29092") \
    .option("subscribe", "events") \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", "false") \
    .load()

parsed_df = kafka_df.select(
    from_json(col("value").cast("string"), event_schema).alias("data")
).select("data.*")

print("Starting streaming query...")
query = parsed_df.writeStream \
    .foreachBatch(upsert_batch) \
    .outputMode("update") \
    .option("checkpointLocation", "/app/checkpoints/events_checkpoint") \
    .start()

query.awaitTermination()