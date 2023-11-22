#!/bin/bash

# Note: the use of sudo for docker commands is bad practice.
# It was necessary for me to run docker with the nvidia-container-toolkit.
# Adapt the scipt to your needs; remove sudo if possible.

# Stop services
sudo docker compose down

# Clear persisted data
# list volumes via: sudo docker volume ls | grep borg-dqn
sudo docker volume rm borg-dqn_model_store
sudo docker volume rm borg-dqn_redis-data
sudo docker volume rm borg-dqn_esdata

# Rebuild images
sudo docker compose build env_agent
sudo docker compose build mem_monitor

# Start services
sudo docker compose up