from loguru import logger

from src.transition import Transition, serialize_transition

from ._redis_thread import RedisThread


class RedisProducerThread(RedisThread):
    def __init__(self, *args, **kwargs):
        self.mem_capacity = kwargs.pop("mem_capacity", 500_000)
        super().__init__(*args, **kwargs)

    def add_transition(self, transition: Transition) -> None:
        with self.condition:
            self.queue.put(transition)
            self.condition.notify_all()

    def _run_once(self) -> None:
        transition = self.queue.get(block=True)
        self.redis_put_transition(transition)

    def redis_put_transition(self, transition: Transition) -> None:
        try:
            self.client.lpush(self.KEY, serialize_transition(transition))
            self.client.ltrim(self.KEY, 0, self.mem_capacity - 1)  # emulate FIFO queue
            logger.debug(f"Pushed transition to Redis: {transition}")
        except Exception as e:
            logger.error(f"Failed to push transition to Redis: {e}")
