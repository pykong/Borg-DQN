class EpsilonDecayStrategy:
    def __init__(
        self,
        epsilon: float = 1.0,
        epsilon_min: float = 0.1,
        epsilon_step: float = 0.001,
        decay_start: int = 0,
    ):
        self._step_count = 0
        self.epsilon = epsilon
        self.epsilon_step = epsilon_step
        self.epsilon_min = epsilon_min
        self.decay_start = decay_start

    def __call__(self) -> float:
        self._step_count += 1
        if self._step_count >= self.decay_start:
            self.epsilon -= self.epsilon_step
            self.epsilon = max(self.epsilon, self.epsilon_min)
        return self.epsilon
