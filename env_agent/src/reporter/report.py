from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Report:
    container_id: UUID
    step_count: int
    reward: float
    epsilon: float
    loss: float
    done: bool
    # timestamp: datetime | None = None

    # def __post_init__(self):
    #     self.timestamp = datetime.now()
