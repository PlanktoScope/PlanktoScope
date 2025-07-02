.PHONY: all clean setup test developer-mode
.DEFAULT_GOAL := setup

setup:
	sudo apt install -y golang --no-install-recommends
	GOBIN=~/.local/bin go install github.com/mrtazz/checkmake/cmd/checkmake@latest
	pipx install poetry==2.1.3 --force
	git submodule update --init
	make -C node-red setup
	make -C controller setup
	make -C segmenter setup
	make -C os setup
	make -C documentation setup

test:
	checkmake Makefile
	make -C node-red test
	make -C controller test
	make -C segmenter test
	make -C os test
	make -C documentation test

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

# consider using just instead of make https://github.com/casey/just
