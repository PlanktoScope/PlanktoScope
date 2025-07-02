setup:
    pipx install poetry==2.1.3 --force
    git submodule update --init
    just --justfile node-red/justfile      setup
    just --justfile controller/justfile    setup
    just --justfile segmenter/justfile     setup
    just --justfile os/justfile            setup
    just --justfile documentation/justfile setup

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

developer-mode:
    git remote set-url origin git@github.com:PlanktoScope/PlanktoScope.git
    git fetch origin
    sudo apt install -y build-essential
    # Install some tools for a nicer command-line experience over ssh
    sudo apt install -y vim byobu git curl tmux
    # Install some tools for dealing with captive portals
    sudo apt install -y w3m lynx
    # Install some tools for troubleshooting networking stuff
    sudo apt install -y net-tools bind9-dnsutils netcat-openbsd nmap avahi-utils
    ./os/developer-mode/install-github-cli.sh
    ./os/developer-mode/install-just.sh
    [ "$CI" != "true" ] && npm install -g zx@8
    [ "$CI" != "true" ] && ./os/developer-mode/configure.mjs
    