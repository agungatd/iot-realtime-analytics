import json
import time
import random
import logging

from kafka import KafkaProducer
from kafka.errors import KafkaError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("iot-producer")

# Configuration
KAFKA_BROKER = 'localhost:9092'  # Kafka broker address (accessible from where you run this script)
KAFKA_TOPIC = 'iot-events'
DEVICE_IDS = [f'device_{i}' for i in range(1, 100)]
COUNTRY_IDS = ['US', 'CA', 'MX', 'GB', 'DE', 'FR', 'JP', 'IN', 'ID']
SEND_INTERVAL = 1  # seconds
MESSAGES_PER_SECOND = 3  # Approximate rate of message generation
GENERATION_DURATION_SECONDS = 300  # How long to run the generator

# Sample dirty strings for testing cleaning
DIRTY_STRINGS = [
    "  needs trim ",
    "UPPERCASE",
    "  mixed Case needs TRIM  ",
    "clean",
    " extra spaces   everywhere ",
    None  # Simulate missing field sometimes
]


def create_kafka_producer(broker=KAFKA_BROKER):
    """Create and return a Kafka producer instance using confluent-kafka."""
    logger.info(f"Attempting to connect to Kafka broker at {broker}...")
    try:
        producer = KafkaProducer(
            bootstrap_servers=broker,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),  # Serialize dict to JSON bytes
            retries=3,  # Retry sending messages upon failure
            acks='all'  # Wait for all replicas to acknowledge
        )
        logger.info(f"Successfully connected to Kafka broker at {broker}")
        return producer
    except Exception as e:
        logger.error(f"Failed to connect to Kafka broker: {e}")
        raise


def generate_iot_event():
    """Generate a mock IoT event with the specified schema."""
    dirty_field = random.choice(DIRTY_STRINGS)

    event = {
        'deviceID': random.choice(DEVICE_IDS),
        'countryID': random.choice(COUNTRY_IDS),
        'timestamp': int(time.time() * 1000),  # Current time in milliseconds since epoch
        'value': round(random.uniform(-10.0, 100.0), 2),  # Random metric value, sometimes negative or zero to test filtering
        "potentiallyDirtyField": dirty_field
    }

    # Randomly remove the dirty field sometimes to test handling missing keys
    if random.random() < 0.1 and "potentiallyDirtyField" in event:
        del event["potentiallyDirtyField"]

    return event


def delivery_report(err, msg):
    """Callback function to check if the message was successfully delivered."""
    if err is not None:
        logger.error("Message delivery failed: %s", err)
    else:
        logger.info("Message delivered to %s [%s]", msg.topic(), msg.partition())


def main():
    producer = create_kafka_producer()
    if not producer:
        return  # Exit if producer couldn't be created

    logger.info(f"Starting data generation for {GENERATION_DURATION_SECONDS} seconds...")
    start_time = time.time()
    message_count = 0
    sleep_interval = 1.0 / MESSAGES_PER_SECOND

    try:
        while (time.time() - start_time) < GENERATION_DURATION_SECONDS:
            event_data = generate_iot_event()

            try:
                # Send the message to Kafka
                future = producer.send(KAFKA_TOPIC, value=event_data, key=event_data['countryID'].encode('utf-8')) # Optional: key by type

                # Block for 'synchronous' sends, helps catch errors immediately (optional)
                # record_metadata = future.get(timeout=10)
                # logger.info(f"Sent message: {event_data} to partition {record_metadata.partition} offset {record_metadata.offset}")

                logger.info(f"Sent: {event_data}")
                message_count += 1

            except KafkaError as e:
                logger.error(f"Error sending message: {e}")
                # Add logic here if you want to handle send failures (e.g., retry, log)
            except Exception as e:
                logger.error(f"An unexpected error occurred during send: {e}")

            # Wait before sending the next message
            time.sleep(sleep_interval)

    except KeyboardInterrupt:
        logger.info("\nGeneration stopped by user.")
    finally:
        if producer:
            logger.info("\nFlushing remaining messages...")
            producer.flush(timeout=10)  # Wait for pending messages to be sent
            logger.info("Closing Kafka producer.")
            producer.close()
        logger.info(f"Total messages sent: {message_count}")


if __name__ == "__main__":
    main()
