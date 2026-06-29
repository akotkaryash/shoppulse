import os
import psycopg2

def get_db_connection():
    # Establishes a connection to the Postgres database.
    return psycopg2.connect(
        host="postgres",
        database=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )

def ensure_unique_constraint():
    # Ensures the event_id column has a unique constraint for the upsert.
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("ALTER TABLE raw.events ADD UNIQUE (event_id);")
        conn.commit()
    except Exception:
        # Constraint likely already exists, ignore
        pass
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

def upsert_batch(batch_df, batch_id):
    
    # The quarantine zone: executes a Postgres-specific idempotent upsert.
    # If we ever switch to Snowflake/BigQuery, we ONLY rewrite this function.
    
    if batch_df.count() == 0:
        return

    # First run initialization (creates table if it doesn't exist)
    db_url = f"jdbc:postgresql://postgres:5432/{os.getenv('POSTGRES_DB')}"
    batch_df.limit(0).write \
        .format("jdbc") \
        .option("url", db_url) \
        .option("dbtable", "raw.events") \
        .option("user", os.getenv('POSTGRES_USER')) \
        .option("password", os.getenv('POSTGRES_PASSWORD')) \
        .option("driver", "org.postgresql.Driver") \
        .mode("ignore") \
        .save()

    ensure_unique_constraint()

    # The actual Upsert Logic
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Convert Spark DF to list of tuples for quick execution
        records = [tuple(row) for row in batch_df.collect()]
        
        execute_batch_sql = """
            INSERT INTO raw.events (event_id, user_key, product_key, event_type, quantity, amount, event_ts)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (event_id) DO NOTHING;
        """
        cur.executemany(execute_batch_sql, records)
        conn.commit()
        print(f"Batch {batch_id}: Upserted {len(records)} records to raw.events")
        
    except Exception as e:
        print(f"Error during upsert: {e}")
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()