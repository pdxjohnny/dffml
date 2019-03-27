#!/usr/bin/env bash
set -e

function run_plugin() {
  python setup.py install && cd "$PLUGIN" && coverage run setup.py test && cd -

  if [ "x$PLUGIN" = "x." ]; then
    ./scripts/create.sh feature travis_test_feature
    ./scripts/create.sh model travis_test_model
  fi
}

function run_changelog() {
  # Only run this check on pull requests
  if [ "x$TRAVIS_PULL_REQUEST" == "xfalse" ]; then
    exit 0
  fi
  # Ensure the number of lines added in the changelog is not 0
  added_to_changelog=$(git diff origin/master --numstat -- CHANGELOG.md \
    | awk '{print $1}')
  if [ "x$added_to_changelog" == "x" ] || [ "$added_to_changelog" -eq 0 ]; then
    echo "No changes to CHANGELOG.md" >&2
    exit 1
  fi
}

function run_whitespace() {
  export whitespace=$(mktemp -u)
  function rmtempfile () {
    rm -f "$whitespace"
  }
  trap rmtempfile EXIT
  ( find dffml -type f -name \*.py -exec grep -EHn " +$" {} \; ) 2>&1 \
    | tee "$whitespace"
  lines=$(wc -l < "$whitespace")
  if [ "$lines" -ne 0 ]; then
    echo "Trailing whitespace found" >&2
    exit 1
  fi
}

function run_demo() {
  GPG_KEY_URL="https://alpinelinux.org/keys/ncopa.asc"
  ALPINE_ISO_URL="http://dl-cdn.alpinelinux.org/alpine/v3.9/releases/x86_64/alpine-virt-3.9.2-x86_64.iso"
  ALPINE_ISO_URL="http://dl-cdn.alpinelinux.org/alpine/v3.9/releases/x86_64/alpine-standard-3.9.2-x86_64.iso"

  RET_PWD="$PWD"
  mkdir -p ".ci/cache"
  cd ".ci/cache"

  function cleanup () {
    cd "${RET_PWD}"
    if [ -d "${TMP_MNT_DIR}" ]; then
      export again=1
      while [ "$again" -eq 1 ]; do
        # Unmount image
        sudo sync
        ( sudo umount "${TMP_MNT_DIR}" && \
          rm -rf "${TMP_MNT_DIR}" ) \
          && export again=0 \
        || \
        export again=1
      done
    fi
    if [ -b "${LOOP}" ]; then
      sudo losetup -d "${LOOP}"
    fi
  }

  trap cleanup EXIT

  IMAGE="clear.iso"

  # Download the image
  if [ ! -f ${IMAGE} ]; then
    latest=$(curl -sSL https://download.clearlinux.org/latest)
    curl -sSL https://download.clearlinux.org/current/clear-${latest}-kvm.img.xz \
      | unxz - > ${IMAGE}
  fi

  if [ ! -f OVMF.fd ]; then
    curl -o OVMF.fd -sSL 'https://download.clearlinux.org/image/OVMF.fd'
  fi

  if [ ! -f vgabios.bin ]; then
    curl -o vgabios.bin -sSL 'https://github.com/copy/v86/raw/master/bios/vgabios.bin'
  fi

  if [ ! -f v86_all.js ]; then
    curl -o v86_all.js -sSL 'https://copy.sh/v86/build/v86_all.js'
  fi

  # Mount image
  LOOP=$(sudo losetup --find --show ${IMAGE})
  TMP_MNT_DIR=$(mktemp -d)
  sudo partprobe ${LOOP}
  sudo mount -o rw ${LOOP}p3 ${TMP_MNT_DIR}

  if [ "x${http_proxy}" != "x" ]; then
    # Resolve proxy server IP address before entering chroot, if set
    proxy_server=$(sed -e 's/.*:\/\///g' -e 's/:.*//g' <<<"${http_proxy}")
    proxy_host=$(nslookup "${proxy_server}" | grep Address: | tail -n 1 | \
      awk '{print $NF}')
    export http_proxy=$(sed -e "s/${proxy_server}/${proxy_host}/g" \
                        <<<"${http_proxy}")
    export https_proxy=$(sed -e "s/${proxy_server}/${proxy_host}/g" \
                        <<<"${https_proxy}")
    export socks_proxy=$(sed -e "s/${proxy_server}/${proxy_host}/g" \
                        <<<"${socks_proxy}")
    export HTTP_PROXY=$http_proxy
    export HTTPS_PROXY=$https_proxy
    export SOCKS_PROXY=$socks_proxy
  fi

  # Add proxy services
  sudo install ../demo.sh ${TMP_MNT_DIR}/usr/bin/
  sudo -E chroot ${TMP_MNT_DIR} /usr/bin/demo.sh

  cp "${IMAGE}" "${RET_PWD}/demo/"
  cp "OVMF.fd" "${RET_PWD}/demo/"
  cp "vgabios.bin" "${RET_PWD}/demo/"
  cp "v86_all.js" "${RET_PWD}/demo/"
}

if [ "x$PLUGIN" != "x" ]; then
  run_plugin
elif [ "x$CHANGELOG" != "x" ]; then
  run_changelog
elif [ "x$WHITESPACE" != "x" ]; then
  run_whitespace
elif [ "x$DEMO" != "x" ]; then
  run_demo
fi
