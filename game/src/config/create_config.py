from envclasses import load_env

from .config import Config


def create_config() -> Config:
    config = Config()
    load_env(config, prefix="CONFIG_")
    return config
