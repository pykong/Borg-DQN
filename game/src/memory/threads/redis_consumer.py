from loguru import logger

from src.transition import deserialize_transition
from random import randint
from ._redis_thread import RedisThread


class RedisConsumerThread(RedisThread):
    def _run_once(self) -> None:
        """Check for new items in Redis and move them to the queue."""
        self.condition.wait_for(lambda: not self.redis_empty() or not self.running)
        if not self.queue.full() and not self.redis_empty():
            for st in self.redis_random_transitions():
                transition = deserialize_transition(st)
                self.queue.put(transition)
                logger.debug(f"Added transition to queue: {transition}")

    def redis_random_transitions(self) -> list[bytes]:
        try:
            mem_size = self.client.llen(self.KEY)
            indexes = [randint(0, mem_size) for _ in range(16)]
            return [self.client.lindex(self.KEY, i) for i in indexes]
        except Exception as e:
            logger.error(f"Failed to get random transitions from Redis: {e}")
            return []

    def redis_empty(self) -> bool:
        try:
            return self.client.llen(self.KEY) == 0
        except Exception as e:
            logger.error(f"Failed to check if Redis is empty: {e}")
            return True
