#!/usr/bin/env bash
set -ex

if [ "x${VIRTUAL_ENV}" != "x" ]; then
  deactivate
fi

PYTHON=${PYTHON:-"python3"}

if [ "x${USER}" == "x" ]; then
  export USER=user
fi

export VIRTUAL_ENV_DIR=$(mktemp -d)

"${PYTHON}" -m venv "${VIRTUAL_ENV_DIR}"
. "${VIRTUAL_ENV_DIR}/bin/activate"

export HOME=$(mktemp -d)

if [ -d "/home/${USER}/.cache/pip" ]; then
  export TARGET="/home/${USER}/.cache/pip"
fi

mkdir -p "${HOME}/.cache"
mkdir -p "${HOME}/.local/bin"

export PATH="${HOME}/.local/bin:${PATH}"

if [ "x${1}" == "x" ]; then
  exec bash
else
  exec ./.ci/run.sh ${1}
fi
