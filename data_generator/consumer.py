import json
from confluent_kafka import Consumer, KafkaException
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("iot-consumer")

# Configuration
KAFKA_BROKER = 'kafka:9092'
KAFKA_TOPIC = 'iot-events'

def create_kafka_consumer():
    """Create and return a Kafka consumer instance."""
    conf = {
        'bootstrap.servers': KAFKA_BROKER,
        'group.id': 'iot-consumer-group',
        'auto.offset.reset': 'earliest',
    }
    try:
        consumer = Consumer(conf)
        consumer.subscribe([KAFKA_TOPIC])
        logger.info("Connected to Kafka broker at %s", KAFKA_BROKER)
        return consumer
    except Exception as e:
        logger.error("Failed to connect to Kafka broker: %s", e)
        raise

def main():
    consumer = create_kafka_consumer()
    try:
        logger.info("Listening for messages on topic '%s'...", KAFKA_TOPIC)
        while True:
            msg = consumer.poll(1.0)  # Wait for 1 second for new messages
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaException._PARTITION_EOF:
                    # End of partition event
                    logger.info("Reached end of partition")
                else:
                    logger.error("Error while consuming: %s", msg.error())
            else:
                event = json.loads(msg.value().decode('utf-8'))
                logger.info("Received event: %s", event)
    except KeyboardInterrupt:
        logger.info("Shutting down consumer...")
    finally:
        consumer.close()
        logger.info("Consumer stopped.")

if __name__ == "__main__":
    main()