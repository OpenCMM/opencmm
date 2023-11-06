FROM python:3.11-slim

# Install poetry
ENV POETRY_HOME=/opt/poetry
RUN python3 -m venv $POETRY_HOME
RUN $POETRY_HOME/bin/pip install poetry==1.5.1
RUN $POETRY_HOME/bin/poetry --version

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

COPY . /app
WORKDIR /app

# Install production dependencies.
RUN $POETRY_HOME/bin/poetry install --without dev

CMD exec $POETRY_HOME/bin/poetry run gunicorn --bind :$PORT --workers 4 --threads 8 --timeout 0 -k uvicorn.workers.UvicornWorker server.main:app