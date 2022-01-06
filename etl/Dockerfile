# syntax=docker/dockerfile:1

FROM python:3.9-alpine

RUN apk update && apk add postgresql-dev gcc musl-dev libffi-dev bash

WORKDIR /etl
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

WORKDIR /airflow/home
ENV AIRFLOW_HOME=/airflow/home
COPY airflow/ .

WORKDIR /etl
COPY . .

CMD ["airflow", "standalone"]
