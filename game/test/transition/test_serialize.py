from src.transition import deserialize_transition, serialize_transition

from .utils import assert_transitions_equal, create_random_transition


def test_serialization_equivalence():
    transition1 = create_random_transition()
    message = serialize_transition(transition1)
    transition2 = deserialize_transition(message)
    assert_transitions_equal(transition1, transition2)
