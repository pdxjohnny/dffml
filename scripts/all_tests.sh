#!/usr/bin/env bash
set -xe

if [ "x${NO_STRICT}" != "x" ]; then
  set +e
fi

SRC_ROOT=${SRC_ROOT:-"${PWD}"}
PYTHON=${PYTHON:-"python3.7"}

PLUGINS=("${SRC_ROOT}/" \
	"${SRC_ROOT}/model/tensorflow" \
	"${SRC_ROOT}/model/scratch" \
	"${SRC_ROOT}/model/scikit" \
	"${SRC_ROOT}/examples/shouldi" \
	"${SRC_ROOT}/feature/git" \
	"${SRC_ROOT}/feature/auth" \
	"${SRC_ROOT}/service/http" \
	"${SRC_ROOT}/source/mysql")
for CURR in ${PLUGINS[@]}; do
  cd "${CURR}"
  "${PYTHON}" setup.py test
  exit_code=$?
  if [ "x${exit_code}" == "x0" ]; then
    echo "[PASS]: ${CURR}"
  else
    echo "[FAIL]: ${CURR}"
  fi
	cd -
done
