import json
import time
import random
import logging
from confluent_kafka import Producer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("iot-producer")

# Configuration
KAFKA_BROKER = 'kafka:9092'
KAFKA_TOPIC = 'iot-events'
DEVICE_IDS = [f'device_{i}' for i in range(1, 100)]
SEND_INTERVAL = 1  # seconds

def create_kafka_producer():
    """Create and return a Kafka producer instance using confluent-kafka."""
    conf = {
        'bootstrap.servers': KAFKA_BROKER,
    }
    try:
        producer = Producer(conf)
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

def delivery_report(err, msg):
    """Callback function to check if the message was successfully delivered."""
    if err is not None:
        logger.error("Message delivery failed: %s", err)
    else:
        logger.info("Message delivered to %s [%s]", msg.topic(), msg.partition())

def main():
    producer = create_kafka_producer()
    try:
        while True:
            event = generate_iot_event()
            producer.produce(
                topic=KAFKA_TOPIC,
                value=json.dumps(event).encode('utf-8'),
                callback=delivery_report
            )
            logger.info("Produced event: %s", event)
            producer.poll(0)  # Serve delivery callback queue
            time.sleep(SEND_INTERVAL)
    except KeyboardInterrupt:
        logger.info("Shutting down producer...")
    finally:
        producer.flush()
        logger.info("Producer stopped.")

if __name__ == "__main__":
    main()