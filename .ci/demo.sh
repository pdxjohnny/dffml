#!/usr/bin/env bash
set -xe

swupd bundle-add python-basic

python --version

python -m pip install "dffml[git,tensorflow]"
