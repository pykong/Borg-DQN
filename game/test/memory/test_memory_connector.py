from test.transition.utils import assert_transitions_equal, create_random_transition
from unittest.mock import MagicMock, patch

import pytest

from src.memory import MemoryConnector
from src.transition import Transition


# Create a test instance of MemoryConnector
@pytest.fixture(scope="function")
def memory_connector():
    with patch(
        "src.memory.threads.redis_producer.RedisProducerThread.start",
        MagicMock(),
    ), patch(
        "src.memory.threads.redis_consumer.RedisConsumerThread.start",
        MagicMock(),
    ):
        connector = MemoryConnector({})
    return connector


# def test_start_threads(mock_consumer_thread):
#     # Given initialized threads
#     # When MemoryConnector is initialized
#     # Then both producer and consumer threads should start
#     mock_producer_thread.start.assert_called_once()
#     mock_consumer_thread.start.assert_called_once()


def test_send_transition(memory_connector):
    # Given a transition
    transition = create_random_transition()

    # When send_transition is called
    memory_connector.send_transition(transition)

    # Then the transition should be added to the producer queue and set as last_transition
    assert not memory_connector.producer_queue.empty()
    assert_transitions_equal(transition, memory_connector.last_transition)


def test_sample_transitions(memory_connector):
    # Given a filled consumer queue and last_transition
    transitions = [create_random_transition() for _ in range(10)]
    memory_connector.last_transition = transitions[0]
    for trans in transitions:
        memory_connector.consumer_queue.put(trans)

    # When sample_transitions is called
    sample = memory_connector.sample_transitions()

    # Then it should return a batch of transitions, padded with last_transition if needed
    assert len(sample) == memory_connector.batch_size
    assert all(isinstance(t, Transition) for t in sample)


def test_sample_transitions_raises_exception(memory_connector):
    # Given an unset last_transition
    memory_connector.last_transition = None

    # When sample_transitions is called
    # Then it should raise a ValueError
    with pytest.raises(ValueError):
        memory_connector.sample_transitions()


def test_sample_transitions_with_enough_elements(memory_connector):
    # Given a filled consumer queue and last_transition
    transitions = [
        create_random_transition() for _ in range(memory_connector.batch_size)
    ]
    memory_connector.last_transition = transitions[0]
    for trans in transitions:
        memory_connector.consumer_queue.put(trans)

    # When sample_transitions is called
    sample = memory_connector.sample_transitions()

    # Then it should return a batch of transitions with size equal to batch_size
    assert len(sample) == memory_connector.batch_size
    assert all(isinstance(t, Transition) for t in sample)


def test_sample_transitions_with_insufficient_elements(memory_connector):
    # Given a consumer queue with fewer than (batch_size - 1) elements and a last_transition
    transitions = [
        create_random_transition() for _ in range(memory_connector.batch_size // 2)
    ]
    memory_connector.last_transition = create_random_transition()
    for trans in transitions:
        memory_connector.consumer_queue.put(trans)

    # When sample_transitions is called
    sample = memory_connector.sample_transitions()

    # Then the returned list should be padded with last_transition to reach batch_size
    assert len(sample) == memory_connector.batch_size
    assert all(isinstance(t, Transition) for t in sample[:-1])
    assert all(
        t == memory_connector.last_transition
        for t in sample[-(memory_connector.batch_size - len(transitions)) :]
    )


def test_sample_transitions_with_no_elements(memory_connector):
    # Given a consumer queue with zero elements and a last_transition
    memory_connector.last_transition = create_random_transition()

    # When sample_transitions is called
    sample = memory_connector.sample_transitions()

    # Then the returned list should be entirely made up of last_transition
    assert len(sample) == memory_connector.batch_size
    assert all(t == memory_connector.last_transition for t in sample)
    # Then the returned list should be entirely made up of last_transition
    assert len(sample) == memory_connector.batch_size
    assert all(t == memory_connector.last_transition for t in sample)
