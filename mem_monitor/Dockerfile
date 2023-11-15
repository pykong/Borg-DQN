
# Stage 2: Configuring base image
FROM simbachain/poetry-3.11 AS base

WORKDIR /mem_monitor

COPY pyproject.toml /mem_monitor
COPY poetry.lock /mem_monitor

RUN python -m pip install --upgrade pip && \
    poetry config virtualenvs.create false && \
    poetry install --without dev,test --no-root

# Stage 2: Production environment with source code
FROM base AS production
COPY src/ /mem_monitor/src
RUN poetry install --without dev,test

CMD ["poetry", "run", "monitor"]
