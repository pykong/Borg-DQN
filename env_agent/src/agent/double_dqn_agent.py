import random
from copy import deepcopy
from functools import wraps
from pathlib import Path
from typing import Any, Callable, NamedTuple, Optional, Self

import lightning.pytorch as pl
import numpy as np
import torch
import torch.nn.functional as F
import torch.optim as optim
from loguru import logger
from torch import Tensor, nn

from src.transition import Transition

# configure torch
torch.autograd.set_detect_anomaly(False)  # type: ignore
torch.autograd.profiler.emit_nvtx(enabled=False)
torch.autograd.profiler.profile(enabled=False)


class Minibatch(NamedTuple):
    states: torch.Tensor
    actions: torch.Tensor
    rewards: torch.Tensor
    next_states: torch.Tensor
    dones: torch.Tensor


def get_torch_device() -> torch.device:
    """Provide best possible device for running PyTorch."""
    if torch.cuda.is_available():
        logger.info("Using CUDA")
        torch.backends.cudnn.benchmark = True  # type: ignore
        return torch.device("cuda")
    else:
        logger.warning("CUDA not available, using CPU")
        return torch.device("cpu")


def update_target_network(f: Callable) -> Callable:
    """
    Return decorator for target model update logic.

    Args:
        f (Callable): The function to decorate.

    Returns:
        Callable: The decorated function.
    """

    @wraps(f)
    def wrapper(self: "DoubleDQNAgent", *args, **kwargs) -> Any:
        self.step_counter += 1
        if self.step_counter % self.target_net_update_interval == 0:
            logger.debug("Updating target network")
            self.step_counter = 0
            self.target_net = deepcopy(self.policy_net)
        return f(self, *args, **kwargs)

    return wrapper


class DoubleDQNAgent(pl.LightningModule):
    def __init__(
        self: Self,
        state_shape: tuple[int, int, int],
        action_space: int,
        net: nn.Sequential | None,
        alpha: float = 0.001,
        gamma: float = 0.99,
        target_net_update_interval: int = 4_000,
        **kwargs: Optional[Any],
    ):
        super().__init__()

        self.gamma = gamma
        self.target_net_update_interval = target_net_update_interval
        self.action_space = action_space
        self.device_: torch.device = get_torch_device()
        self.policy_net = self.__init_net(state_shape, action_space, self.device_, net)
        self.target_net = deepcopy(self.policy_net)
        self.optimizer = optim.RMSprop(self.policy_net.parameters(), lr=alpha)
        self.scaler = torch.cuda.amp.GradScaler(enabled=True)  # type:ignore
        self.step_counter: int = 0

    def __init_net(
        self,
        state_shape: tuple[int, int, int],
        action_space: int,
        device_: torch.device,
        net: nn.Sequential,
    ) -> nn.Sequential:
        """Build linear deep net."""
        channel_dim, x_dim, y_dim = state_shape
        input_dims = channel_dim * x_dim * y_dim
        net = net or nn.Sequential(
            # fc 1
            nn.Flatten(),
            nn.Linear(input_dims, 512),
            nn.ReLU(),
            # fc 2
            nn.Linear(512, 384),
            nn.ReLU(),
            # fc 3
            nn.Linear(384, 64),
            nn.ReLU(),
            # fc 4
            nn.Linear(64, 16),
            nn.ReLU(),
            # output
            nn.Linear(16, action_space),
        )
        net = net.to(device=device_)
        net = net.to(memory_format=torch.channels_last)  # type:ignore
        return net

    @update_target_network
    def replay(self: Self, sample: list[Transition]) -> float:
        logger.debug("Replaying minibatch")

        # convert the minibatch to a more convenient format
        states, actions, rewards, next_states, dones = self._encode_minibatch(sample)

        # mask dones
        dones = 1 - dones

        # predict Q-values for the initial states
        q_out = self.forward(states)

        # state_action_values
        q_a = q_out.gather(1, actions)

        # calc max q prime value
        max_q_prime = self._calc_max_q_prime(next_states)

        # compute the expected Q values (expected_state_action_values)
        target = rewards + self.gamma * max_q_prime * dones

        # calc losses
        with torch.cuda.amp.autocast(enabled=True):  # type:ignore
            losses = F.smooth_l1_loss(q_a, target)

        # update the weights
        self._update_weights(losses)

        # return losses
        return losses.mean().item()

    @torch.no_grad()
    def _calc_max_q_prime(self: Self, next_states: Tensor) -> float:
        return self.target_net(next_states).max(1)[0].unsqueeze(1)

    def _encode_minibatch(self: Self, transitions: list[Transition]) -> Minibatch:
        def encode_array(states: list[np.ndarray]) -> Tensor:
            return torch.from_numpy(np.array(states)).to(self.device_).float()

        def encode_number(number: list[float] | list[int]) -> Tensor:
            return torch.tensor(number, device=self.device_).unsqueeze(-1)

        states = [t.state for t in transitions]
        actions = [t.action for t in transitions]
        rewards = [t.reward for t in transitions]
        next_states = [t.next_state for t in transitions]
        dones = [float(t.done) for t in transitions]

        return Minibatch(
            states=encode_array(states),
            actions=encode_number(actions),
            rewards=encode_number(rewards),
            next_states=encode_array(next_states),
            dones=encode_number(dones),
        )

    def _update_weights(self: Self, losses: Tensor) -> None:
        self.optimizer.zero_grad(set_to_none=True)
        self.scaler.scale(losses).backward()  # type: ignore
        # Unscales the gradients of optimizer's assigned params in-place
        # https://h-huang.github.io/tutorials/recipes/recipes/amp_recipe.html#inspecting-modifying-gradients-e-g-clipping
        self.scaler.unscale_(self.optimizer)
        nn.utils.clip_grad_norm_(self.policy_net.parameters(), max_norm=1.0)  # type: ignore
        self.scaler.step(self.optimizer)
        self.scaler.update()

    @torch.no_grad()
    def act(self: Self, state: np.ndarray, *, epsilon: float) -> int:
        """Take random action with probability epsilon, else take best action."""
        if np.random.rand() <= epsilon:
            return random.randrange(self.action_space)
        state = torch.from_numpy(state).to(self.device_)
        act_values = self.forward(state.unsqueeze(0))
        return act_values.argmax().item()

    def forward(self: Self, x: Tensor) -> Tensor:
        with torch.cuda.amp.autocast(enabled=True):  # type:ignore
            return self.policy_net(x)  # type:ignore

    def load(self: Self, name: Path) -> None:
        """Load model from path.

        Args:
            name (Path): The path to the model file.
        """
        logger.info(f"Loading model: {name}")
        checkpoint = torch.load(name)
        self.policy_net.load_state_dict(checkpoint["policy_net"])
        self.target_net.load_state_dict(checkpoint["target_net"])
        self.optimizer.load_state_dict(checkpoint["optimizer"])
        self.scaler.load_state_dict(checkpoint["scaler"])

    def save(self: Self, name: Path) -> None:
        """Save model to path.

        Args:
            name (Path): The file path to save the model to.
        """
        logger.info(f"Saving model: {name}")
        checkpoint = {
            "policy_net": self.policy_net.state_dict(),
            "target_net": self.target_net.state_dict(),
            "optimizer": self.optimizer.state_dict(),
            "scaler": self.scaler.state_dict(),
        }
        torch.save(checkpoint, name)
