.PHONY: all clean setup test
.DEFAULT_GOAL := setup

setup:
	sudo apt install -y shellcheck

test:
	shellcheck **/*.sh
