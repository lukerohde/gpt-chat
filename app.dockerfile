# BASIC INSTALL
FROM python:3.11-buster
RUN apt-get update -qq
RUN apt-get install -qq python3-pip python3-dev libpq-dev postgresql-client
RUN apt-get install -y ca-certificates curl gnupg

# Enable WesCorp man-in-the-middle surveillance 
COPY .zscaler/ZscalerRootCertificate-2048-SHA256.crt /usr/local/share/ca-certificates/ZscalerRootCertificate-2048-SHA256.crt
RUN update-ca-certificates
ENV NODE_EXTRA_CA_CERTS=/usr/local/share/ca-certificates/ZscalerRootCertificate-2048-SHA256.crt
ENV PIP_CERT=/usr/local/share/ca-certificates/ZscalerRootCertificate-2048-SHA256.crt

RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/trusted.gpg.d/nodesource.gpg
RUN echo "deb [signed-by=/etc/apt/trusted.gpg.d/nodesource.gpg] https://deb.nodesource.com/node_18.x nodistro main" > /etc/apt/sources.list.d/nodesource.list
RUN apt-get update && apt-get install -y nodejs
RUN npm install npm@latest -g

RUN adduser --disabled-password --gecos "" pyuser
USER pyuser
ENV PATH=/home/pyuser/.local/bin:"$PATH"

RUN mkdir -p /home/pyuser/app
WORKDIR /home/pyuser/app

COPY ./app/requirements.txt /home/pyuser/app/requirements.txt
RUN --mount=type=cache,target=/home/pyuser/.cache/pip pip install --user -r ./requirements.txt

COPY ./app /home/pyuser/app
RUN mkdir -p /home/pyuser/app/memory
RUN mkdir -p /home/pyuser/app/logs
