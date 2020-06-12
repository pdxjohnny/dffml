FROM python:3.7

ENV PATH="/opt/conda/minicondapy37/bin:${PATH}"

WORKDIR /usr/src/dffml

COPY ./.ci/deps.sh ./.ci/deps.sh
COPY *setup.py .

# RUN ./.ci/deps.sh all
