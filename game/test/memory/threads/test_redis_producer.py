from queue import Queue
from test.transition.utils import create_random_transition
from unittest.mock import Mock

import pytest

from src.memory.threads.redis_producer import RedisProducerThread
from src.transition import serialize_transition


# Mock Redis client to simulate Redis operations
@pytest.fixture(scope="function")
def mock_redis_client():
    return Mock()


# Create a test instance of RedisProducerThread
@pytest.fixture(scope="function")
def producer_thread(mock_redis_client):
    queue = Queue(8)
    redis_config = {"host": "localhost", "port": 6379}
    producer = RedisProducerThread(redis_config, queue)
    producer.client = mock_redis_client
    return producer


def test_run_once_adds_to_redis(producer_thread, mock_redis_client):
    # Given a transition in the queue
    transition = create_random_transition()
    producer_thread.queue.put(transition)

    # When _run_once is called
    producer_thread._run_once()

    # Then the transition should be added to Redis
    mock_redis_client.lpush.assert_called_once_with(
        "transitions", serialize_transition(transition)
    )

    # Then the Redis trim command should be called
    mock_redis_client.ltrim.assert_called_once_with("transitions", 0, 499_999)


def test_run_once_skips_when_queue_is_empty(mock_redis_client):
    # Given an empty queue
    assert mock_redis_client.queue.empty()

    # When _run_once is called
    mock_redis_client._run_once()

    # Then no Redis operation should be called
    mock_redis_client.lpush.assert_not_called()


def test_terminate_stops_thread(producer_thread):
    # When the terminate function is called
    producer_thread._terminate(None, None)

    # Then the thread should stop running
    assert not producer_thread.running
