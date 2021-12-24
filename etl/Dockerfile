# syntax=docker/dockerfile:1

FROM python:3.10-alpine

RUN apk update && apk add postgresql-dev gcc musl-dev

WORKDIR /etl
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

