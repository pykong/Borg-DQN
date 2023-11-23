import signal
from abc import ABC, abstractmethod
from queue import Queue
from threading import Condition, Thread
from typing import Any

import redis

from src.transition import Transition


class RedisThread(ABC, Thread):
    """RedisConsumerThread class.

    This class pulls Transistions from Redis and puts them into a thread-safe queue.
    """

    KEY = "transitions"

    def __init__(self, redis_config: dict[str, Any], queue: Queue[Transition]) -> None:
        """Initialize RedisThread.

        Args:
            queue (Queue): The queue for communicatoing transitions.
        """
        Thread.__init__(self)
        self.queue = queue

        self.client = redis.Redis(host="redis", port=6379, decode_responses=False)
        self.condition = Condition()
        self.running = True
        signal.signal(signal.SIGTERM, self._terminate)
        signal.signal(signal.SIGINT, self._terminate)

    def _terminate(self, *_: Any) -> None:
        """Terminate the thread gracefully."""
        with self.condition:
            self.running = False
            self.condition.notify()

    def run(self) -> None:
        """Run the consumer thread indefinitely."""
        with self.condition:
            while self.running:
                self._run_once()

    @abstractmethod
    def _run_once(self) -> None:
        raise NotImplementedError("RedisThread._run_once no implemented.")
