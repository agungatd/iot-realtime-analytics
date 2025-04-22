import json
import time
import random
import logging
from kafka import KafkaProducer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("iot-producer")

# Configuration
KAFKA_BROKER = 'kafka:9092'
KAFKA_TOPIC = 'iot-events'
DEVICE_IDS = ['device_1', 'device_2', 'device_3', 'device_4', 'device_5']
SEND_INTERVAL = 1  # seconds

def create_kafka_producer():
    """Create and return a Kafka producer instance."""
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        logger.info("Connected to Kafka broker at %s", KAFKA_BROKER)
        return producer
    except Exception as e:
        logger.error("Failed to connect to Kafka broker: %s", e)
        raise

def generate_iot_event():
    """Generate a mock IoT event with the specified schema."""
    return {
        'device_id': random.choice(DEVICE_IDS),
        'timestamp': int(time.time() * 1000),  # Current time in milliseconds
        'metric': round(random.uniform(0, 100), 2)  # Random metric value
    }

def main():
    producer = create_kafka_producer()
    try:
        while True:
            event = generate_iot_event()
            producer.send(KAFKA_TOPIC, value=event)
            logger.info("Produced event: %s", event)
            time.sleep(SEND_INTERVAL)
    except KeyboardInterrupt:
        logger.info("Shutting down producer...")
    finally:
        producer.flush()
        producer.close()
        logger.info("Producer stopped.")

if __name__ == "__main__":
    main()