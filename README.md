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

<p align="center">
    <a href="#readme">
        <img alt="Title picture" src="https://raw.githubusercontent.com/pykong/Borg-DQN/main/docs/img/title_picture.png">
        <!-- Title picture credits: Benjamin Felder -->
        <!-- Title picture created using DALL-E -->
    </a>
</p>

# Borg-DQN

**A Stream-Fueled Hive Mind for Reinforcement Learning.**

This project originated as the implementation of the portfolio assignment for the data engineering module DLMDSEDE02 at the International University of Applied Sciences. It demonstrates how to build a streaming data-intensive application with a machine-learning focus.

Borg-DQN presents a distributed approach to reinforcement learning centered around a **shared replay
memory**. Echoing the collective intelligence of the [Borg](https://memory-alpha.fandom.com/wiki/Borg_Collective)
from the Star Trek universe, the system enables individual agents to tap into a hive-mind-like pool of communal
experiences to enhance learning efficiency and robustness.

This system adopts a containerized microservices architecture enhanced with real-time streaming capabilities.
Within game containers, agents employ Deep Q-Networks (DQN) for training on the Atari Pong environment
from OpenAI Gym. The replay memory resides in a separate container, consisting of a Redis Queue, wherein
agents interface via protocol buffer messages.

The architecture continuously streams agents' learning progress and replay memory metrics to Kafka,
enabling instant analysis and visualization of learning trajectories and memory growth on a Kibana
dashboard.

## Gettings Started

### Requirements

The execution of Borg-DQN requires a working installation of `Docker`, as well as the `nvidia-container-toolkit` to pass through CUDA acceleration to the game container instances. Refer to the respective documentation for installation instructions:

- [Install Docker Engine](https://docs.docker.com/engine/install/)
- [Installing the NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

The development furthermore requires a working Python 3.11 interpreter and `poetry` for dependency management:

- [Python Releases](https://www.python.org/downloads/)
- [Poetry installation](https://python-poetry.org/docs/#installation)

### Starting Up

To start the application run from the root directory:

```sh
docker compose up
```

Observe the learning progress and memory growth on the [live dashboard](http://localhost:5601/app/dashboards#/view/6c58f7d0-71c5-11ee-bccb-318d0f7f71cb?_g=(filters:!(),refreshInterval:(pause:!t,value:0),time:(from:now-15m,to:now))).

To start the application with multiple game containers run:

```sh
docker compose up --scale env_agent=3
```

The [Elasticsearch indices](http://localhost:9200/_cat/indices?pretty) can also be looked into.

## Architecture

The application follows an infrastructure-as-code (`IaC`) approach, wherein individual services run inside Docker containers, whose configuration and interconnectivity are defined in a [`compose.yaml`](https://github.com/pykong/Borg-DQN/blob/readme/compose.yaml) at its root directory.

<p align="center">
    <a href="#readme">
        <img alt="Architecture diagram" src="https://raw.githubusercontent.com/pykong/Borg-DQN/main/docs/img/architecture.svg">
        <!-- Architecture diagram credits: Benjamin Felder -->
    </a>
</p>

In the following, there is a short overview of each component of the application.

### Game Container

The game container encapsulates an Atari Pong environment (OpenAI gym) and a double deep Q-network agent (using PyTorch). The code is adapted from [MERLIn](https://github.com/pykong/merlin), an earlier reinforcement learning project by [pykong](https://github.com/pykong).

<p align="center">
    <a href="#readme">
        <img alt="Pong screenshot" src="https://raw.githubusercontent.com/pykong/Borg-DQN/main/docs/img/pong.png">
        <!-- Pong screenshot credits: Benjamin Felder -->
    </a>
</p>

<!-- configuration -->

#### Serializing Game Transitions

[Protocol Buffers](https://protobuf.dev/)

```.proto
syntax = "proto3";

package transition.proto;

message Transition {
    bytes state = 1;
    uint32 action = 2;
    float reward = 3;
    bytes next_state = 4;
    bool done = 5;
    ...
}
```

### Replay Memory

The shared replay memory employs Redis to hold game transitions. Redis is not only performant but also allows storing the transitions as serialized protobuf messages, due to its byte-safe characteristics.

### Memory Monitor

The memory monitor is a Python microservice that periodically polls the Redis shared memory for transition count and memory usage statistics and publishes those under a dedicated Kafka topic.

### Kafka

[Apache Kafka](https://kafka.apache.org/) is a distributed streaming platform that excels in handling high-throughput, fault-tolerant messaging. In Borg-DQN, Kafka serves as the middleware that decouples the data-producing game environments from the consuming analytics pipeline, allowing for robust scalability and the flexibility to introduce additional consumers without architectural changes. Specifically, Kafka channels log to two distinct topics, 'training_log' and 'memory_monitoring', both serialized as JSON, ensuring structured and accessible data for any downstream systems.

### ELK Stack

The [ELK stack](https://www.elastic.co/en/elastic-stack), comprising `Elasticsearch`, `Logstash`, and `Kibana`, serves as a battle-tested trio for managing, processing, and visualizing data in real-time, making it ideal for observing training progress and replay memory growth in Borg-DQN. Elasticsearch acts as a search and analytics engine with robust database characteristics, allowing for quick retrieval and analysis of large datasets. Logstash seamlessly ingests data from Kafka through a declarative pipeline configuration, eliminating the need for custom code. Kibana leverages this integration to provide a user-customizable dashboard, all components being from Elastic, ensuring compatibility and stability.

<p align="center">
    <a href="#readme">
        <img alt="Kibana screenshot" src="https://raw.githubusercontent.com/pykong/Borg-DQN/main/docs/img/kibana.png">
        <!-- Kibana screenshot credits: Benjamin Felder -->
    </a>
</p>

### Development

<!-- [multi-stage builds](https://docs.docker.com/build/building/multi-stage/) -->

## Plans

- [ ] Create external documentation, preferably using [MkDocs](https://www.mkdocs.org/)
- [ ] Allow game container instances to be individually configured (e.g. different epsilon values to address the exploitation-exploration tradeoff)
- [ ] Upgrade the replay memory to one featuring prioritization of transitions.

## Contributions Welcome

If you like Borg-DQN and want to develop it further, feel free to fork and open any pull request. 🤓

## Links

1. [Borg Collective](https://memory-alpha.fandom.com/wiki/Borg_Collective)
2. [Docker Engine](https://docs.docker.com/engine/)
3. [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/)
4. [Poetry Docs](https://python-poetry.org/docs/)
5. [Redis Docs](https://redis.io/docs/)
6. [Apache Kafka](https://kafka.apache.org/)
7. [ELK Stack](https://www.elastic.co/en/elastic-stack)
8. [Protocol Buffers](https://protobuf.dev/)
9. [Massively Parallel Methods for Deep Reinforcement Learning](https://arxiv.org/pdf/1507.04296.pdf)
   - a more intricate architecture than Borg-DQN, also featuring a shared replay memory
