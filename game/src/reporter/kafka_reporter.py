import signal
from queue import Queue
from threading import Condition, Thread
from typing import Any

from confluent_kafka import Producer
from loguru import logger

from .report import Report


class KafkaReporter:
    TOPIC = "train_reports"

    def __init__(self, kafka_config):
        self.queue = Queue()
        self.producer = Producer(kafka_config)
        self.condition = Condition()
        signal.signal(signal.SIGTERM, self._terminate)
        signal.signal(signal.SIGINT, self._terminate)
        self.running = True
        self.thread = Thread(target=self._run)
        self.thread.start()

    def _terminate(self, *_: Any) -> None:
        """Terminate the thread gracefully."""
        with self.condition:
            self.running = False
            self.condition.notify()

    def send_report(self, report: Report) -> None:
        logger.info(report)
        self.queue.put(report)

    def _run(self) -> None:
        with self.condition:
            while self.running:
                report = self.queue.get(block=True)
                self._push_report(report)

    def _push_report(self, report: Report) -> None:
        try:
            self.producer.produce(self.TOPIC, value=report.to_json())  # type:ignore
            self.producer.flush()
        except Exception as e:
            logger.error(f"Failed to send report to Kafka: {e}", exc_info=True)
        else:
            logger.debug(f"Sent report to Kafka: {report}")
