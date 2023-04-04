# BASIC INSTALL
FROM python:3.11-buster
RUN apt-get update -qq
RUN apt-get install -qq python3-pip python3-dev libpq-dev postgresql-client

RUN curl -sL https://deb.nodesource.com/setup_16.x | bash
RUN apt-get install -y nodejs
RUN npm install npm@latest -g

RUN adduser pyuser
USER pyuser
ENV PATH=/home/pyuser/.local/bin:"$PATH"

RUN mkdir -p /home/pyuser/app
WORKDIR /home/pyuser/app

COPY ./app/requirements.txt /home/pyuser/app/requirements.txt
RUN --mount=type=cache,target=/home/pyuser/.cache/pip pip install --user -r ./requirements.txt

COPY ./app /home/pyuser/app
RUN mkdir -p /home/pyuser/app/memory

