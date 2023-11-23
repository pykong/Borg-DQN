import random
from datetime import datetime
from uuid import uuid4

from src.reporter import Report


def create_random_report() -> Report:
    return Report(
        container_id=uuid4(),
        reward=random.randrange(0, 21),
        step_count=random.randrange(0, 1000),
        epsilon=random.random(),
        loss=random.random(),
        done=random.choice([True, False]),
    )
