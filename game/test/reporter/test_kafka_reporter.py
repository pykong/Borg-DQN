from test.reporter.utils import create_random_report
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.reporter.kafka_reporter import KafkaReporter


# Mock Kafka producer to simulate Kafka operations
@pytest.fixture(scope="function")
def mock_kafka_producer():
    return Mock()


# Create a test instance of KafkaReporter
@pytest.fixture(scope="function")
def kafka_reporter(mock_kafka_producer):
    kafka_config = {"bootstrap.servers": "localhost:9092"}
    with patch("threading.Thread.start", MagicMock()):
        reporter = KafkaReporter(kafka_config)
        reporter.producer = mock_kafka_producer
        return reporter


def test_send_report_adds_to_queue(kafka_reporter):
    # Given a report
    report = create_random_report()

    # When send_report is called
    kafka_reporter.running = False
    with kafka_reporter.condition:
        kafka_reporter.send_report(report)

    # Then the report should be added to the queue
    assert not kafka_reporter.queue.empty()
    actual = kafka_reporter.queue.get()
    assert report == actual


def test_run_once_pushes_report(kafka_reporter, mock_kafka_producer):
    # Given a report in the queue
    report = create_random_report()
    kafka_reporter.queue.put(report)

    # When _run_once is called
    kafka_reporter.running = False
    with kafka_reporter.condition:
        kafka_reporter._run_once()

    # Then the report should be pushed to Kafka
    assert mock_kafka_producer.produce.call_count == 1
    mock_kafka_producer.produce.assert_called_with(
        KafkaReporter.TOPIC,
        value=report.to_json(),
    )


def test_terminate_stops_thread(kafka_reporter):
    # When the terminate function is called
    kafka_reporter._terminate(None, None)

    # Then the thread should stop running
    assert not kafka_reporter.running
