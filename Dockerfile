FROM python:3.8-slim-bullseye

ENV POETRY_VIRTUALENVS_CREATE=false
ADD ./pyproject.toml ./poetry.lock /app/
WORKDIR /app
RUN apt-get update && apt-get install -y firefox
RUN pip install poetry==1.1.13
RUN poetry install

ADD . /app
RUN poetry install
CMD ["python", "-u", "nagasaki/trader/main.py"]