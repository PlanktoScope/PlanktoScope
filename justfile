export PATH := x"${PATH}:/home/$USER/.local/bin"

setup:
    git submodule update --init
    just --justfile node-red/justfile      setup
    just --justfile controller/justfile    setup
    just --justfile segmenter/justfile     setup
    just --justfile os/justfile            setup
    just --justfile documentation/justfile setup

setup-dev:
    just --justfile node-red/justfile      setup-dev
    just --justfile controller/justfile    setup-dev
    just --justfile segmenter/justfile     setup-dev
    just --justfile os/justfile            setup-dev
    just --justfile documentation/justfile setup-dev
    sudo apt install -y golang
    GOBIN=~/.local/bin go install github.com/rhysd/actionlint/cmd/actionlint@v1.7

base:
    curl -fsSL https://deb.nodesource.com/setup_22.x -o /tmp/nodesource_setup.sh
    sudo -E bash /tmp/nodesource_setup.sh
    sudo apt install -y pipx git nodejs
    pipx install poetry==2.1.3 --force
    pipx ensurepath

format:
    just --fmt --unstable
    just --justfile node-red/justfile      format
    just --justfile controller/justfile    format
    just --justfile segmenter/justfile     format
    just --justfile os/justfile            format
    just --justfile documentation/justfile format

test:
    just --fmt --check --unstable
    just --justfile node-red/justfile      test
    just --justfile controller/justfile    test
    just --justfile segmenter/justfile     test
    just --justfile os/justfile            test
    just --justfile documentation/justfile test
    actionlint --shellcheck="" # TODO: Enable shelcheck for actionlint

developer-mode:
    just setup-dev
    git remote set-url origin git@github.com:PlanktoScope/PlanktoScope.git
    git fetch origin
    # https://www.damirscorner.com/blog/posts/20210423-ChangingUrlsOfGitSubmodules.html
    git submodule sync
    git submodule update --init --recursive --remote
    sudo apt install -y build-essential
    # Install some tools for a nicer command-line experience over ssh
    sudo apt install -y vim byobu git curl tmux lsof ripgrep
    # Install some tools for dealing with captive portals
    sudo apt install -y w3m lynx
    # Install some tools for troubleshooting networking stuff
    sudo apt install -y net-tools bind9-dnsutils netcat-openbsd nmap avahi-utils
    ./os/developer-mode/install-github-cli.sh
    ./os/developer-mode/install-just.sh
    npm install -g zx@8
    ./os/developer-mode/configure.mjs

# We run setup and setup-dev twice to ensure it is idempotent

# TODO: Run developer-mode (twice)
ci: base setup setup-dev test format setup setup-dev
