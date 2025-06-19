import logging
import os

from confluent_kafka import Producer


def get_kafka_producer():
    if not hasattr(get_kafka_producer, "_producer"):
        kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
        producer_conf = {
            "bootstrap.servers": kafka_servers,
            "client.id": "market-data-producer",
            "acks": "all",
            "retries": 3,
        }
        get_kafka_producer._producer = Producer(producer_conf)
    return get_kafka_producer._producer


def delivery_report(err, msg):
    if err is not None:
        logging.error(f"Message delivery failed: {err}")
    else:
        logging.info(
            f"Message delivered to {msg.topic()} [{msg.partition()}] offset {msg.offset()}"
        )


def publish_price_event(event: dict):
    try:
        producer = get_kafka_producer()
        producer.produce(
            topic="price-events",
            key=event["symbol"],
            value=str(event),
            callback=delivery_report,
        )
        producer.flush()
    except Exception as e:
        logging.error(f"Failed to produce message: {e}")
        raise
