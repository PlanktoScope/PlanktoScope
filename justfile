export PATH := x"${PATH}:/home/$USER/.local/bin"

default: base setup

base:
    sudo cp os/debian-backports.sources /etc/apt/sources.list.d/
    # TODO https://github.com/nodesource/distributions/wiki/Repository-Manual-Installation
    curl -fsSL https://deb.nodesource.com/setup_22.x -o /tmp/nodesource_setup.sh
    sudo -E bash /tmp/nodesource_setup.sh
    sudo apt update
    sudo apt install -y pipx git nodejs
    pipx ensurepath
    pipx install poetry==2.1.3 --force
    npm config set prefix /home/pi/.local

setup:
    just --justfile node-red/justfile      setup
    just --justfile controller/justfile    setup
    just --justfile segmenter/justfile     setup
    just --justfile os/justfile            setup
    just --justfile documentation/justfile setup
    just --justfile lib/justfile           setup
    just --justfile backend/justfile       setup
    just --justfile frontend/justfile      setup

setup-dev:
    just --justfile node-red/justfile      setup-dev
    just --justfile controller/justfile    setup-dev
    just --justfile segmenter/justfile     setup-dev
    just --justfile os/justfile            setup-dev
    just --justfile documentation/justfile setup-dev
    just --justfile lib/justfile           setup-dev
    just --justfile backend/justfile       setup-dev
    just --justfile frontend/justfile      setup-dev
    ./os/developer-mode/install-actionlint.sh
    ./os/developer-mode/install-config-file-validator.sh

format:
    find . -type f -name 'justfile' -exec just --fmt --unstable --justfile {} ';'

test:
    find . -type f -name 'justfile' -exec just --fmt --check --unstable --justfile {} ';'
    just --justfile node-red/justfile      test
    just --justfile controller/justfile    test
    just --justfile segmenter/justfile     test
    just --justfile os/justfile            test
    just --justfile documentation/justfile test
    just --justfile lib/justfile           test
    just --justfile backend/justfile       test
    just --justfile frontend/justfile      test
    actionlint --shellcheck="" # TODO: Enable shelcheck for actionlint

developer-mode: setup-dev
    git remote set-url origin git@github.com:PlanktoScope/PlanktoScope.git
    git fetch origin
    sudo apt install -y build-essential
    # Install some tools for a nicer command-line experience over ssh
    sudo apt install -y vim byobu git curl tmux lsof ripgrep
    # Install some tools for dealing with captive portals
    sudo apt install -y w3m lynx
    # Install some tools for troubleshooting networking stuff
    sudo apt install -y net-tools bind9-dnsutils netcat-openbsd nmap avahi-utils
    ./os/developer-mode/install-github-cli.sh
    cd ./os/developer-mode && npm install
    ./os/developer-mode/configure.mjs

reset: base setup
    rm /home/pi/PlanktoScope/config.json
    rm /home/pi/PlanktoScope/hardware.json
    sudo reboot

# We run setup and setup-dev twice to ensure it is idempotent

# TODO: Run developer-mode (twice)
ci: base setup setup-dev test format setup setup-dev
