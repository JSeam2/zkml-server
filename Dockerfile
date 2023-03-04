# pull official base image
FROM python:3.8

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Rust related stuff
# Update new packages
RUN apt-get update

# install rust
RUN apt-get install -y \
    build-essential \
    curl

# Get Rust
RUN curl https://sh.rustup.rs -sSf | bash -s -- --default-toolchain nightly -y

# copy project
COPY ./ezkl /app/ezkl

# Set new work directory
WORKDIR /app/ezkl

# Build ezkl
RUN ~/.cargo/bin/cargo build --release

# Set new work directory
WORKDIR /app

# install dependencies
RUN set -ex && \
    pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN set -ex && \
    pip install -r requirements.txt

# copy project
COPY . /app


