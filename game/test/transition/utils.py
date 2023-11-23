import numpy as np
import pytest

from src.transition import Transition


def generate_binary_images_stack(
    image_shape: tuple[int, int] = (64, 64), num_images: int = 4
) -> np.ndarray:
    """
    Generate a stack of binary images.

    Args:
        image_shape (tuple): The shape of each image as (width, height).
        num_images (int): Number of images to be stacked.

    Returns:
        np.ndarray: Stack of binary images of shape (num_images, width, height).
    """
    # generate random binary images
    binary_images = [
        np.random.choice([0, 1], size=image_shape) for _ in range(num_images)
    ]

    # stack the images along the first axis
    return np.stack(binary_images, axis=0)


def create_random_transition() -> Transition:
    state = generate_binary_images_stack()
    action = np.random.randint(1, 4)
    reward = np.random.ranf()
    next_state = generate_binary_images_stack()
    done = bool(np.random.choice([True, False]))
    return Transition(state, action, reward, next_state, done)


def assert_transitions_equal(
    expected: Transition, actual: Transition, epsilon: float = 1e-6
) -> None:
    """
    Assert that two Transition instances are equal.

    Args:
        trans1 (Transition): The first Transition instance.
        trans2 (Transition): The second Transition instance.
        epsilon (float): Tolerance level for floating point comparisons.
    """
    assert isinstance(expected.state, np.ndarray)
    assert isinstance(actual.state, np.ndarray)
    assert np.array_equal(expected.state, actual.state)
    assert expected.action == actual.action
    assert expected.reward == pytest.approx(actual.reward, abs=epsilon)
    assert isinstance(expected.next_state, np.ndarray)
    assert isinstance(actual.next_state, np.ndarray)
    assert np.array_equal(expected.next_state, actual.next_state)
    assert expected.done == actual.done
