FROM python:3.8

ENV PATH="/opt/conda/minicondapy38/bin:${PATH}"

WORKDIR /usr/src/dffml

COPY ./.ci/deps.sh ./.ci/deps.sh

RUN ./.ci/deps.sh all
