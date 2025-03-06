FROM python:3.9.18-slim-bookworm
COPY . /home
RUN apt-get update && \
apt-get upgrade -y && \
apt-get install -y git
WORKDIR /home
RUN python3 -m pip install .
ENTRYPOINT start
