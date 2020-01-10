FROM gitpod/workspace-full

USER gitpod

RUN sudo apt-get -q update && \
  sudo apt-get install -yq tmux git && \
  curl -sSL "https://github.com/XAMPPRocky/tokei/releases/download/v10.1.1/tokei-v10.1.1-x86_64-unknown-linux-gnu.tar.gz" \
    | tar -xvz && \
  sudo mv tokei /usr/bin/ && \
  sudo rm -rf /var/lib/apt/lists/*
