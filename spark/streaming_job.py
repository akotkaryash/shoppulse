import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, LongType

# Initialize Spark session
# We don't need to specify packages here because we pre-downloaded the necessary packages in the Dockerfile.
spark = SparkSession.builder \
    .appName("ShopPulse_Streaming_Injestion") \
    .conf("spark.sql.shuffle.partitions", "2") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Define the schema for the incoming JSON data
event_schema = StructType([
    StructField("event_id", StringType(), True),
    StructField("user_key", IntegerType(), True),
    StructField("product_key", IntegerType(), True),
    StructField("event_type", StringType(), True),
    StructField("quantity", IntegerType(), True),
    StructField("amount", DoubleType(), True),
    StructField("event_ts", LongType(), True)
])

# Read the streaming data from Kafka
print("Starting to read from Kafka topic 'events'...")
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:29092") \
    .option("subscribe", "events") \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", "false") \
    .load()
    
# Parse the JSON data and apply the schema
parsed_df = kafka_df.select(from_json(col("value").cast("string"), event_schema).alias("data")).select("data.*")

# Database connection properties
db_properties = {
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
    "driver": "org.postgresql.Driver",
    "database": os.getenv("POSTGRES_DB", "shop_pulse"),
}

# Write the streaming data to PostgreSQL
def upsert_to_postgres(batch_df, batch_id):
    """Function to upsert data into PostgreSQL."""

    if batch_df.count() == 0:
        print(f"Batch {batch_id} is empty. Skipping write to PostgreSQL.")
        return
    
    # First, we check if the table exists and create it if it doesn't.
    # We can use the JDBC connection to execute a SQL command to create the table if it doesn't exist.
    batch_df.limit(0).write \
        .format("jdbc") \
        .option("url", f"jdbc:postgresql://postgres:5432/{db_properties['database']}") \
        .option("dbtable", "raw.events") \
        .option("user", db_properties["user"]) \
        .option("password", db_properties["password"]) \
        .option("driver", db_properties["driver"]) \
        .mode("ignore") \
        .save()

    batch_df.createOrReplaceTempView("current_batch")
    
    # Upsert logic: Insert new records and update existing ones based on event_id
    upsert_query = """
        INSERT INTO raw.events (event_id, user_key, product_key, event_type, quantity, amount, event_ts)
        SELECT event_id, user_key, product_key, event_type, quantity, amount, event_ts
        FROM current_batch
        ON CONFLICT (event_id) DO NOTHING;
    """
    
    # We use the underlying psycopg2 driver (via Spark's JVM) or basic JDBC execution.
    # A simpler way in pure PySpark for this sandbox is to use the Postgres connection directly.
    # However, since we want to stick purely to Spark's distributed architecture:
    import psycopg2
    conn = psycopg2.connect(
        host="postgres",
        database=db_properties["database"],
        user=db_properties["user"],
        password=db_properties["password"]
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute("ALTER TABLE raw.events ADD UNIQUE (event_id);")  # Ensure event_id is unique for upsert
            conn.commit()
    except Exception as e:
        print(f"Error ensuring unique constraint on event_id: {e}")
        pass
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            
    try:
        with conn.cursor() as cursor:
            cursor.execute(upsert_query)
            conn.commit()
    except Exception as e:
        print(f"Error during upsert operation: {e}")
        

    # Execute the upsert query
    batch_df.sparkSession.sql(upsert_query)
    print(f"Batch {batch_id} written to PostgreSQL.")


# Start the streaming query
query = parsed_df.writeStream \
    .foreachBatch(upsert_to_postgres) \
    .outputMode("update") \
    .option("checkpointLocation", "/tmp/spark_checkpoint") \
    .start()

query.awaitTermination()