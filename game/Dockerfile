# Stage 1: Base stage with CUDA, Python 3.11, and essential packages
FROM nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04 AS base
WORKDIR /app

# Install Python 3.11
RUN ln -fs /usr/share/zoneinfo/UTC /etc/localtime
RUN DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.11 python3.11-distutils python3.11-dev python3.11-venv python3-pip

# Update pip
RUN python3.11 -m pip install --upgrade pip

# Install poetry
RUN python3.11 -m venv .poetry_venv/
RUN .poetry_venv/bin/pip install -U pip setuptools
RUN .poetry_venv/bin/pip install poetry

# Copy pyproject.toml and install dependencies
COPY pyproject.toml .
COPY poetry.lock .
RUN .poetry_venv/bin/poetry config virtualenvs.create false && \
    .poetry_venv/bin/poetry install --without dev,test --no-root

# Install libgl1 (for cv2)
RUN apt-get update && apt-get install -y libgl1

# Stage 2: Production environment with source code
FROM base AS production
COPY src/ /app/src

# Command to run the application
CMD [".poetry_venv/bin/python", "-m", "src"]
