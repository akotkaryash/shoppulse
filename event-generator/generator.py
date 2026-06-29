import json
import time
import random
from faker import Faker
from confluent_kafka import Producer

fake = Faker()

# 1. Configure a Kafka producer
# Inside Docker, we connect using the service name 'kafka' defined in the docker-compose.yml file.
producer_config = {
    'bootstrap.servers': 'kafka:29092',  # Replace with your Kafka broker address
    'client.id': 'event-generator'
}

producer = Producer(producer_config)
topic = 'events'  # Replace with your Kafka topic name

def delivery_report(err, msg):
    """Callback function to report delivery status."""
    if err is not None:
        print(f"Delivery failed for record {msg.key()}: {err}")
    else:
        print(f"Record {msg.key()} successfully produced to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

def generate_event():
    event_types = ['page_view', 'add_to_cart', 'purchase']
    # 70% chance for 'page_view', 20% for 'add_to_cart', and 10% for 'purchase' to simulate realistic user behavior
    event_type = random.choices(event_types, weights=[0.7, 0.2, 0.1])[0]  # Weighted probabilities for event types

    """Generate a random event with a timestamp and random data."""
    event = {
        'event_id': fake.uuid4(),
        'user_key': random.randint(1, 1000),
        'product_key': random.randint(1, 100),
        'event_type': event_type,
        'quantity': random.randint(1, 5) if event_type in ['add_to_cart', 'purchase'] else 0,
        'amount': round(random.uniform(10.0, 500.0), 2) if event_type == 'purchase' else 0.0,
        'event_ts': int(time.time() * 1000),  # Current timestamp in milliseconds
    }
    return event

if __name__ == "__main__":
    print("Starting event generator...")
    #sleep for 5 seconds to allow Kafka to start up
    time.sleep(5)
    print(f"Producing events to topic '{topic}'...")

    try:
        while True:
            event = generate_event()
            event_json = json.dumps(event).encode('utf-8')  # Convert the event to JSON and encode it to bytes
            # Use producer.poll(0) to ensure that the producer is ready to send messages
            producer.poll(0)
            # Send the event to Kafka
            producer.produce(topic, value=event_json, callback=delivery_report)
            time.sleep(random.uniform(0.5, 2.0))  # Random delay between events to simulate real-time traffic
    except KeyboardInterrupt:
        print("Event generation stopped.")
    finally:
        producer.flush()  # Ensure all messages are sent before exiting
        print("Producer flushed and exiting.")