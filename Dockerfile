# pull official base image
FROM python:3.8.0-slim

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN set -ex && \
    pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN set -ex && \
    pip install -r requirements.txt

# copy project
COPY . /app


