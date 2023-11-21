<p align="center">
    <a href="#readme">
        <img alt="Title picture" src="https://raw.githubusercontent.com/pykong/Borg-DQN/main/docs/img/title_picture.png">
        <!-- Title picture credits: Benjamin Felder -->
        <!-- Title picture created using DALL-E -->
    </a>
</p>
<p align="center">
    <a href="#readme"><img alt="PlaceholderBadge" src="https://badgen.net/static/PyVersion/3.11/purple"></a>
    <a href="#readme"><img alt="PlaceholderBadge" src="https://badgen.net/static/Code-Quality/A+/green"></a>
    <a href="#readme"><img alt="PlaceholderBadge" src="https://badgen.net/static/Black/OK/green"></a>
    <a href="#readme"><img alt="PlaceholderBadge" src="https://badgen.net/static/Coverage/0.0/gray"></a>
    <a href="#readme"><img alt="PlaceholderBadge" src="https://badgen.net/static/MyPy/78.0/blue"></a>
    <a href="#readme"><img alt="PlaceholderBadge" src="https://badgen.net/static/Docs/0.0/gray"></a>
    <a href="https://github.com/pykong/Borg-DQN/main/LICENSE"><img alt="License" src="https://badgen.net/static/license/MIT/blue"></a>
    <a href="#readme"><img alt="PlaceholderBadge" src="https://badgen.net/static/Build/1.0.0/pink"></a>
    <a href="#readme"><img alt="PlaceholderBadge" src="https://badgen.net/static/stars/★★★★★/yellow"></a>
</p>

# Borg-DQN

A Stream-Fueled Hive Mind for Reinforcement Learning.

This project originated as the implementation of the portfolio assignment for the data engineering module DLMDSEDE02 at the International University of Applied Sciences.

<!-- Shared Memory -->
<!-- Demonstrating Streaming App -->

Borg-DQN presents a distributed approach to reinforcement learning centered around a shared replay
memory. Echoing the collective intelligence of the Borg from the Star Trek universe, the system
enables individual agents to tap into a hive-mind-like pool of communal experiences to enhance learning
efficiency and robustness.

This system adopts a containerized microservices architecture enhanced with real-time streaming capabilities.
Within game containers, agents employ Deep Q-Networks (DQN) for training on the Atari Pong environment
from OpenAI Gym. The replay memory resides in a separate container, consisting of a Redis Queue, wherein
agents interface via protocol buffer messages.

The architecture continuously streams agents' learning progress and replay memory metrics to Kafka,
enabling instant analysis and visualization of learning trajectories and memory growth on a Kibana
dashboard.

## Architecture

<p align="center">
    <a href="#readme">
        <img alt="Architecture diagram" src="https://raw.githubusercontent.com/pykong/Borg-DQN/main/docs/img/architecture.svg">
        <!-- Architecture diagram credits: Benjamin Felder -->
    </a>
</p>

## Gettings Started

### Requirements

The execution of Borg-DQN requires a working installation of `Docker``, as well as the` nvidia-container-toolkit`` to passthrough CUDA-acceleration to the container instances. Refer to the respective documentation for installation instructions:

- [Install Docker Engine](https://docs.docker.com/engine/install/)
- [Installing the NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

### Starting Up

<!-- multiple agents -->

```sh
docker compose up
```

Using multiple game containers:

```sh
docker compose up --scale env_agent=3
```

### Development

## Future plans

<!-- individual agent configuration, exploration-exploitation trade-off -->

## Links

<!-- link to MERLIn -->
