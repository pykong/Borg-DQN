import json
import os
import time
from typing import Any

import redis
from confluent_kafka import Producer
from loguru import logger


def get_redis_metrics(r: redis.Redis) -> dict[str, Any] | None:
    """Fetch Redis metrics like length and memory usage.

    Args:
        r (redis.client): Redis client.

    Returns:
        dict[str, Any]: Dictionary containing Redis metrics.
    """
    try:
        info = r.info()
        memory_used = info["used_memory_dataset"]  # type:ignore
        transition_count =  r.llen("transitions")
    except Exception as e:
        logger.error(f"Error polling redis: {e}")
    else:
        return {"memory_used": memory_used, "transition_count": transition_count}


def push_to_kafka(p: Producer, topic: str, data: dict[str, Any]) -> None:
    """Push data to a Kafka topic.

    Args:
        p (Producer): Kafka producer.
        topic (str): Kafka topic name.
        data (dict[str, Any]): Data to be sent.
    """
    try:
        p.produce(topic, value=json.dumps(data))
        p.flush()
    except ConnectionError as e:
        logger.error(f"Could not connect to Kafka: {e}")


def monitor():
    # get polling interval from the environment or use default (1 second)
    polling_interval = int(os.getenv("POLLING_INTERVAL", 1))

    # initialize Redis client
    r = redis.Redis(host="redis", port=6379)

    # initialize Kafka producer
    kafka_conf = {"bootstrap.servers": "kafka:9092"}
    p = Producer(kafka_conf)
    topic = "redis_metrics"

    while True:
        # fetch Redis metrics
        metrics = get_redis_metrics(r)

        # guard against empty metrics
        if metrics:
            # log metrics
            logger.debug(f"Redis metrics: {metrics}")

            # push metrics to Kafka
            push_to_kafka(p, topic, metrics)

        # wait for the next iteration
        time.sleep(polling_interval)
