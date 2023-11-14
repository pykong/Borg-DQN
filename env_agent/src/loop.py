from pathlib import Path
from typing import Final
from uuid import UUID, uuid4

from loguru import logger
from numpy import ndarray

from .agent import DoubleDQNAgent, EpsilonDecayStrategy
from .config import Config
from .environment import PongEnvWrapper
from .memory import MemoryConnector
from .reporter import KafkaReporter, Report
from .transition import Transition

KAFKA_CONFIG = {"bootstrap.servers": "kafka:9092"}
REDIS_CONFIG = {"host": "redis", "port": 6379}
MODEL_SAVE_PATH: Final[Path] = Path("/usr/share/model_store")


def loop(config: Config) -> None:
    # baptize myself
    container_id: Final[UUID] = uuid4()

    # calculate input shape
    input_shape = (1, config.input_dim * config.frame_stack, config.input_dim)

    # init dependencies
    env = PongEnvWrapper(state_dims=(config.input_dim, config.input_dim))
    agent = DoubleDQNAgent(state_shape=input_shape, action_space=env.action_space.n)
    memory = MemoryConnector(redis_config=REDIS_CONFIG)
    epsilon = EpsilonDecayStrategy(epsilon_step=config.epsilon_step)
    reporter = KafkaReporter(KAFKA_CONFIG)

    # declare run_step()
    def run_step(
        step_count: int,
        done: bool,
        state: ndarray,
        epsilon: float,
    ) -> tuple[bool, ndarray]:
        # log
        logger.debug(f"Step {step_count}, done: {done}, epsilon: {epsilon}")

        # init/reset environment
        if done:
            state = env.reset()

        # act & observe
        action = agent.act(state, epsilon=epsilon)
        next_state, reward, done = env.step(action)

        # broadcast transition
        transition = Transition(state, action, reward, next_state, done)
        memory.send_transition(transition)

        # train agent
        sample = memory.sample_transitions()
        loss = agent.replay(sample)

        # send report
        report = Report(
            container_id=container_id,
            step_count=step_count,
            reward=reward,
            epsilon=epsilon,
            loss=loss,
            done=done,
        )
        reporter.send_report(report)

        # return done and next_state
        return done, next_state

    # run main loop
    done = False
    state = env.reset()
    for step_count in range(1, config.steps):
        # run step
        done, state = run_step(
            step_count=step_count,
            done=done,
            state=state,
            epsilon=epsilon(),
        )
        # save model
        if config.model_save_interval and step_count % config.model_save_interval == 0:
            dst = MODEL_SAVE_PATH / f"{container_id}_{step_count}.pt"
            agent.save(dst)
