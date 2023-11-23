from numpy import frombuffer, reshape

import src.transition.proto.transition_pb2 as transition_pb2

from .transition import Transition


def serialize_transition(transition: Transition) -> bytes:
    """Serialize a Transition instance into protobuf bytes.

    Args:
        transition (Transition): The Transition instance to serialize.

    Returns:
        bytes: The serialized protobuf message.
    """
    transition_proto = transition_pb2.Transition(  # type:ignore
        state=transition.state.tobytes(),
        action=transition.action,
        reward=transition.reward,
        next_state=transition.next_state.tobytes(),
        done=transition.done,
        state_shape=list(transition.state.shape),
        state_dtype=str(transition.state.dtype),
        next_state_shape=list(transition.next_state.shape),
        next_state_dtype=str(transition.next_state.dtype),
    )
    return transition_proto.SerializeToString()


def deserialize_transition(data: bytes) -> Transition:
    """Deserializes a Transition instance from protobuf bytes.

    Args:
        data (bytes): The serialized protobuf message.

    Returns:
        Transition: The deserialized Transition instance.
    """
    transition_proto = transition_pb2.Transition()  # type:ignore
    transition_proto.ParseFromString(data)

    state = frombuffer(transition_proto.state, dtype=transition_proto.state_dtype)
    state = reshape(state, transition_proto.state_shape)

    next_state = frombuffer(
        transition_proto.next_state, dtype=transition_proto.next_state_dtype
    )
    next_state = reshape(next_state, transition_proto.next_state_shape)

    return Transition(
        state=state,
        action=transition_proto.action,
        reward=transition_proto.reward,
        next_state=next_state,
        done=transition_proto.done,
    )
