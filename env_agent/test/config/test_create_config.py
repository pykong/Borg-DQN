import pytest

from src.config import Config, LogLevel, create_config

# Parameterized test data: field name, default value, environment value
test_data = [
    ("input_dim", 48, "50"),
    ("frame_stack", 4, "5"),
    ("target_net_update_interval", 1_024, "2000"),
    ("steps", 1_000_000, "1_500_000"),
    ("alpha", 5e-6, "1e-6"),
    ("epsilon_step", 1e-5, "2e-5"),
    ("epsilon_min", 0.1, "0.05"),
    ("gamma", 0.99, "0.98"),
    ("batch_size", 32, "64"),
    # ("model_save_interval", None, "1000"),
    ("log_level", LogLevel.WARNING, "ERROR"),
]


@pytest.mark.parametrize("field,default,env_value", test_data)
def test_create_config_with_env_vars(monkeypatch, field, default, env_value):
    """
    Test if the factory function correctly overrides dataclass fields with environment variables.
    """

    # Create the config object before setting environment variables
    initial_config = create_config()
    initial_value = getattr(initial_config, field)

    # Check if default value is as expected
    assert (
        initial_value == default
    ), f"For field {field}, expected {default} but got {initial_value}"

    # Set environment variable
    monkeypatch.setenv("CONFIG_" + field.upper(), env_value)

    # Create a new config object
    updated_config = create_config()
    updated_value = getattr(updated_config, field)

    # Check if environment variable is correctly applied
    expected_value = type(default)(env_value) if default is not None else int(env_value)
    assert (
        updated_value == expected_value
    ), f"For field {field}, expected {expected_value} but got {updated_value}"
