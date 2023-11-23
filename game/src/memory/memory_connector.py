from queue import Queue
from typing import Any

from src.transition import Transition

from .threads.redis_consumer import RedisConsumerThread
from .threads.redis_producer import RedisProducerThread


class MemoryConnector:
    def __init__(
        self,
        redis_config: dict[str, Any],
        batch_size: int = 32,
    ) -> None:
        self.batch_size = batch_size
        self.last_transition: Transition  # for CER

        # start consumer thread
        self.consumer_queue: Queue[Transition] = Queue(256)
        self.consumer_thread = RedisConsumerThread(redis_config, self.consumer_queue)
        self.consumer_thread.start()

        # start producer thread
        self.producer_queue: Queue[Transition] = Queue(32)
        self.producer_thread = RedisProducerThread(redis_config, self.producer_queue)
        self.producer_thread.start()

    def send_transition(self, transition: Transition) -> None:
        self.last_transition = transition
        self.producer_queue.put(transition, timeout=1)

    def sample_transitions(self) -> list[Transition]:
        if not self.last_transition:
            raise ValueError("last_transition is None or invalid")
        sample_size = min(self.consumer_queue.qsize(), self.batch_size - 1)
        sample = [self.consumer_queue.get() for _ in range(sample_size)]
        pad = [self.last_transition] * (self.batch_size - sample_size)
        return [*sample, *pad]
