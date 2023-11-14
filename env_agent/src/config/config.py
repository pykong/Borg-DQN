from dataclasses import dataclass

from envclasses import envclass

from .log_level import LogLevel


@envclass
@dataclass(frozen=False)
class Config:
    """A configuration object holding all parameters for an experiment.

    Attributes:

    """

    # environment parameters
    input_dim: int = 48
    frame_stack: int = 4

    # agent parameters
    target_net_update_interval: int = 1_024

    # training parameters
    steps: int = 1_000_000
    alpha: float = 5e-6
    epsilon_step: float = 1e-5
    epsilon_min: float = 0.1
    gamma: float = 0.99
    batch_size: int = 32

    # save parameter
    model_save_interval: int | None = None

    # log level
    log_level: LogLevel = LogLevel.WARNING
