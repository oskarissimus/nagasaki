FROM python:3.8-slim-bullseye

ENV POETRY_VIRTUALENVS_CREATE=false
ADD ./pyproject.toml ./poetry.lock /app/
WORKDIR /app
RUN pip install poetry==1.1.13
RUN poetry install --no-dev

ADD . /app
RUN poetry install --no-dev
CMD ["python", "-u", "websocket_logger/main.py"]