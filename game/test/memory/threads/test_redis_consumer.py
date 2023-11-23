from queue import Queue
from test.transition.utils import assert_transitions_equal, create_random_transition
from unittest.mock import Mock

import pytest

from src.memory.threads.redis_consumer import RedisConsumerThread
from src.transition import serialize_transition


# Mock Redis client to simulate Redis operations
@pytest.fixture(scope="function")
def mock_redis_client():
    return Mock()


# Create a test instance of RedisConsumerThread
@pytest.fixture(scope="function")
def consumer_thread(mock_redis_client):
    queue = Queue(8)
    redis_config = {"host": "localhost", "port": 6379}
    consumer = RedisConsumerThread(redis_config, queue)
    consumer.client = mock_redis_client
    return consumer


def test_run_once_adds_to_queue(consumer_thread, mock_redis_client):
    # Given a serialized transition
    transition = create_random_transition()
    serialized_transition = serialize_transition(transition)

    # When Redis has one item
    mock_redis_client.llen.return_value = 1
    mock_redis_client.lindex.return_value = serialized_transition

    # And _run_once is called
    consumer_thread._run_once()

    # Then the item should be added to the queue
    assert not consumer_thread.queue.empty()
    actual = consumer_thread.queue.get()
    assert_transitions_equal(transition, actual)


def test_run_once_skips_when_queue_is_full(consumer_thread, mock_redis_client):
    # Given a full queue
    for _ in range(consumer_thread.queue.maxsize):
        consumer_thread.queue.put(None)

    # And a serialized transition
    transition = create_random_transition()
    serialized_transition = serialize_transition(transition)

    # When Redis has one item
    mock_redis_client.llen.return_value = 1
    mock_redis_client.brpop.return_value = ("transitions", serialized_transition)

    # And _run_once is called
    consumer_thread._run_once()

    # Then no new item should be added to the queue
    assert consumer_thread.queue.full()
    assert all(item is None for item in list(consumer_thread.queue.queue))


def test_terminate_stops_thread(consumer_thread):
    # When the terminate function is called
    consumer_thread._terminate(None, None)

    # Then the thread should stop running
    assert not consumer_thread.running

    # Then the thread should stop running
    assert not consumer_thread.running
