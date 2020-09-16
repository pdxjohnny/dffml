#!/usr/bin/env bash
#
# This file is responsible for installing any dependencies needed by the various
# DFFML plugins, the docs, and DFFML itself.

# set -e to exit this script if any programs run by this script fail
# set -x to echo everything we do before we do it
set -ex

export PLUGIN="${1}"

# =========================== BEGIN INTER DEPENDENCIES =========================
#
# Core plugins which depend on other code plugins should install those core
# plugins that they depend on here

if [ "x${PLUGIN}" == "xmodel/tensorflow_hub" ]; then
  python -m pip install -U -e "./model/tensorflow"
fi

if [[ "x${PLUGIN}" == "xoperations/deploy" ]]; then
  python -m pip install -U -e "./feature/git"
fi

if [[ "x${PLUGIN}" == "xoperations/nlp" ]]; then
  python -m pip install -U -e "./model/tensorflow"
fi

if [ "x${PLUGIN}" = "xexamples/shouldi" ]; then
  python -m pip install -U -e "./feature/git"
fi

# ===========================  END  INTER DEPENDENCIES =========================
