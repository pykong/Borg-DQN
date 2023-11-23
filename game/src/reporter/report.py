from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from dataclasses_json import dataclass_json


# TODO: freeze
@dataclass_json
@dataclass
class Report:
    container_id: UUID
    step_count: int
    reward: float
    epsilon: float
    loss: float
    done: bool
