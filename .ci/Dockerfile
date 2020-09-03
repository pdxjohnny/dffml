FROM python:3.7-buster

# ========================== BEGIN DOCKER SETUP ================================
#
# Docker related setup

# The version of python we're using in pyXY format (changes with base image)
ARG PYTHON_SHORT_VERSION=py37

# The location we should install conda to
ARG CONDA_INSTALL_LOCATION=/opt/conda

# Set current working directory
WORKDIR /usr/src/dffml

# Copy over CI related scripts
COPY .ci/conda.sh .ci/conda.sh
# Copy over development dependencies
COPY requirements-dev.txt requirements-dev.txt

# Tell apt that we can't answer it's questions if it has any (time zone is a
# common one)
ENV DEBIAN_FRONTEND noninteractive

# ==========================  END  DOCKER SETUP ================================


# ========================== BEGIN GLOBAL DEPENDENCIES =========================
#
# Dependencies that are applicable to the main package and plugins, or just must
# be installed first.

# Install conda because some plugins have dependencies which are only available
# on conda (those listed first). Also because we need to install those packages
# for the integration tests for the main package (.) and when generating the
# docs. Has to be installed first because other packages will be installed into
# the environment that we set up using it (essentially a virtualenv)
RUN .ci/conda.sh ${CONDA_INSTALL_LOCATION}
# Install and upgrade
# pip and setuptools, which are used to install other packages
# twine, which is used to upload released packages to PyPi
RUN python -m pip install --upgrade pip setuptools twine
# Install main package so that other packages have access to it
RUN python -m pip install -U -r requirements-dev.txt

# ==========================  END  GLOBAL DEPENDENCIES =========================


# =========================== BEGIN TEST DEPENDENCIES ==========================
#
# Dependencies for specific plugins only used when running the tests for those
# plugins. Not when generating docs or running main package integration tests

# feature/git
# operations/deploy
RUN curl -sSL https://github.com/XAMPPRocky/tokei/releases/download/v9.1.1/tokei-v9.1.1-x86_64-unknown-linux-gnu.tar.gz | \
    tar xvz -C "/usr/bin/" && \
  apt-get update && \
  apt-get install -y \
    git \
    subversion \
    cloc \
    openssl && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# source/mysql
RUN . /etc/os-release && \
  export NAME=$(echo $NAME | sed -e 's/ .*//g') && \
  echo "deb http://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/${NAME}_${VERSION_ID}/ /" | tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list && \
  curl -v "https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/${NAME}_${VERSION_ID}/Release.key" | apt-key add - && \
  apt-get update && \
  apt-get install -y \
    iptables \
    podman && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* && \
  mkdir -p /etc/containers && \
  echo -e "[registries.search]\nregistries = ['docker.io', 'quay.io']" | tee /etc/containers/registries.conf
# podman pull mariadb:10

# ===========================  END  TEST DEPENDENCIES ==========================


# ========================== BEGIN INSTALL DEPENDENCIES ========================
#
# Dependencies which must be installed prior to installing a plugin. If a plugin
# requires something be installed, it must also ensure that those dependencies
# get installed when we are running the tests for the main package (.) or the
# docs (docs). Each if statement seen here will check if we are running tests
# for the plugin, main package, or docs, and install if any of those conditions
# are true.

# model/vowpalWabbit
# .
# docs
RUN . "${CONDA_INSTALL_LOCATION}/miniconda${PYTHON_SHORT_VERSION}/bin/activate" base && \
  conda install -y -c conda-forge vowpalwabbit

# model/daal4py
# .
# docs
RUN . "${CONDA_INSTALL_LOCATION}/miniconda${PYTHON_SHORT_VERSION}/bin/activate" base && \
  if [ "${PYTHON_SHORT_VERSION}" != "py38" ]; then conda install -y -c intel daal4py==2020.1 daal==2020.1; fi

#####################3
#####################3
#       TODO
# move get-pip to conda
#####################3
#####################3

# operations/nlp
RUN . "${CONDA_INSTALL_LOCATION}/miniconda${PYTHON_SHORT_VERSION}/bin/activate" base && \
  conda install -y -c conda-forge spacy && \
  curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
  python get-pip.py && \
  python -m spacy download en_core_web_sm

# model/autosklearn
# .
# docs
RUN . "${CONDA_INSTALL_LOCATION}/miniconda${PYTHON_SHORT_VERSION}/bin/activate" base && \
  apt-get update && \
  apt-get install -y \
    build-essential \
    swig && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* && \
  python -m pip install pyrfr cython && \
  curl https://raw.githubusercontent.com/automl/auto-sklearn/master/requirements.txt | \
    xargs -n 1 -L 1 python -m pip install

# ==========================  END  INSTALL DEPENDENCIES ========================


# =========================== BEGIN INTER DEPENDENCIES =========================
#
# Core plugins which depend on other code plugins should install those core
# plugins that they depend on here

# if [ "x${PLUGIN}" == "xmodel/tensorflow_hub" ]; then
#   python -m pip install -U -e "./model/tensorflow"
# fi
#
# if [[ "x${PLUGIN}" == "xmodel/spacy" ]]; then
#   conda install -y -c conda-forge spacy
#   python -m spacy download en_core_web_sm
# fi
#
# if [[ "x${PLUGIN}" == "xoperations/deploy" ]]; then
#   python -m pip install -U -e "./feature/git"
# fi
#
# if [[ "x${PLUGIN}" == "xoperations/nlp" ]]; then
#   conda install -y -c conda-forge spacy
#   python -m spacy download en_core_web_sm
#   python -m pip install -U -e "./model/tensorflow"
# fi
#
# if [ "x${PLUGIN}" = "xexamples/shouldi" ]; then
#   python -m pip install -U -e "./feature/git"
# fi

# ===========================  END  INTER DEPENDENCIES =========================
