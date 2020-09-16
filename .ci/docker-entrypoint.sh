#!/usr/bin/env bash
set -ex

if [ "x${VIRTUAL_ENV}" != "x" ]; then
  deactivate
fi

PYTHON=${PYTHON:-"python3"}

if [ "x${USER}" == "x" ]; then
  export USER=user
fi

if [ "x${HOME}" == "x" ]; then
  export HOME="/tmp/home/${USER}"
  mkdir -p "${HOME}"
fi

echo "#!/usr/bin/env bash" > /tmp/cmd.sh
chmod 755 /tmp/cmd.sh
runit () {
  exec /tmp/cmd.sh
}

CONDA_INSTALL_LOCATION=/opt/conda
. "${CONDA_INSTALL_LOCATION}/miniconda${PYTHON_SHORT_VERSION}/bin/activate" base

if [ "x${1}" == "x" ]; then
  echo "exec bash" >> /tmp/cmd.sh
else
  echo "./.ci/run.sh ${1}" >> /tmp/cmd.sh
fi

# source ./.ci/deps.sh "${1}"

# Copy pre-downloaded containers to user accessable location
mkdir -p "${HOME}/.local/share/"
cp -rup /var/lib/containers "${HOME}/.local/share/containers"
chown "${USER}:${USER}" -R "${HOME}/.local/share/containers"
# Refresh bolt_state.db to not point to /var/run/libpod/ for it's lock file
# Do this by removing the .db
rm "${HOME}/.local/share/containers/storage/libpod/bolt_state.db"
# And re-pulling the image to update the .db. Image won't be transfered over the
# network, just revalidated and the .db updated.
podman pull mariadb:10.5.5

runit
