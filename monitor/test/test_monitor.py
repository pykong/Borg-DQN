import json
from unittest.mock import MagicMock, patch


from src.monitor import get_redis_metrics, push_to_kafka


@patch("redis.Redis")
def test_get_redis_metrics(mock_redis):
    mock_redis_instance = MagicMock()
    mock_redis_instance.info.return_value = {"used_memory": 1000}
    mock_redis_instance.llen.return_value = 5
    mock_redis.return_value = mock_redis_instance

    expected_metrics = {"memory_used": 1000, "transition_count": 5}
    assert get_redis_metrics(mock_redis_instance) == expected_metrics


@patch("src.monitor.Producer")
def test_push_to_kafka(mock_producer):
    mock_producer_instance = MagicMock()
    mock_producer.return_value = mock_producer_instance

    topic = "test_topic"
    data = {"test_key": "test_value"}

    push_to_kafka(mock_producer_instance, topic, data)

    mock_producer_instance.produce.assert_called_once_with(topic, value=json.dumps(data))
    mock_producer_instance.flush.assert_called_once()
