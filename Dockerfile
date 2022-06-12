FROM python:3.8-slim-bullseye

RUN set -x \
   && apt update \
   && apt upgrade -y \
   && apt install -y \
       firefox-esr

ENV POETRY_VIRTUALENVS_CREATE=false
ADD ./pyproject.toml ./poetry.lock /app/
WORKDIR /app
RUN pip install poetry==1.1.13

ADD . /app
RUN poetry install --no-dev
CMD ["python", "-u", "nagasaki/trader/main.py"]