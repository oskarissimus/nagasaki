FROM python:3.8-slim-buster

ADD . /app
WORKDIR /app
RUN pip install poetry==1.1.8
ENV POETRY_VIRTUALENVS_CREATE=false
RUN poetry install
CMD ["python", "-u", "nagasaki/trader/main.py"]