from src.agent.epsilon_decay import EpsilonDecayStrategy


def test_call_decreases_epsilon():
    # Given an EpsilonDecayStrategy with epsilon=1.0 and epsilon_step=0.001
    strategy = EpsilonDecayStrategy(epsilon=1.0, epsilon_step=0.001)

    # When the strategy is called 1000 times
    for _ in range(1000):
        strategy()

    # Then the epsilon value should be 0.1
    assert strategy() == 0.1


def test_call_does_not_decrease_epsilon_before_decay_start():
    # Given an EpsilonDecayStrategy with epsilon=1.0, epsilon_step=0.001, and decay_start=1000
    strategy = EpsilonDecayStrategy(epsilon=1.0, epsilon_step=0.001, decay_start=1000)

    # When the strategy is called 999 times
    for _ in range(999):
        strategy()

    # Then the epsilon value should still be 1.0
    assert strategy.epsilon == 1.0


def test_call_does_not_decrease_epsilon_below_epsilon_min():
    # Given an EpsilonDecayStrategy with epsilon=0.1, epsilon_min=0.1, and epsilon_step=0.001
    strategy = EpsilonDecayStrategy(epsilon=0.1, epsilon_min=0.1, epsilon_step=0.001)

    # When the strategy is called 1000 times
    for _ in range(1000):
        strategy()

    # Then the epsilon value should still be 0.1
    assert strategy.epsilon == 0.1
