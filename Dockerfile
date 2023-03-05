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
RUN apt-get install -y \
    build-essential \
    curl

# copy project
COPY ./requirements.txt /app/requirements.txt

# install dependencies
RUN set -ex && \
    pip install --upgrade pip
RUN set -ex && \
    pip install -r requirements.txt

# install solc
RUN set -ex && \
    pip install solc-select; \
    solc-select install 0.8.17; \
    solc-select use 0.8.17

# for building ezkl separately
# Get Rust
# RUN curl https://sh.rustup.rs -sSf | bash -s -- --default-toolchain nightly -y

# # copy project
# COPY ./ezkl /app/ezkl

# # Build ezkl
# RUN ~/.cargo/bin/cargo build --release --manifest-path ./ezkl/Cargo.toml

# copy rest of project
COPY . /app

CMD ["gunicorn", "-w 1", "-t 1000", "-b 0.0.0.0:5000", "app:app"]


