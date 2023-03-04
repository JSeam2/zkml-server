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

# for building ezkl separately
# Get Rust
# RUN curl https://sh.rustup.rs -sSf | bash -s -- --default-toolchain nightly -y

# # copy project
# COPY ./ezkl /app/ezkl

# # Build ezkl
# RUN ~/.cargo/bin/cargo build --release --manifest-path ./ezkl/Cargo.toml

# copy rest of project
COPY . /app

CMD ["gunicorn", "-w 4", "-b 0.0.0.0:5000", "app:app"]


