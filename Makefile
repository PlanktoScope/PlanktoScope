.PHONY: all clean setup test developer-mode
.DEFAULT_GOAL := setup

setup:
	sudo apt install golang --no-install-recommends
	go install github.com/mrtazz/checkmake/cmd/checkmake@latest
	pipx install poetry==2.1.3
	git submodule update --init
	make -C node-red setup
	make -C controller setup
	make -C segmenter setup
	make -C os setup
	make -C documentation setup

test:
	~/go/bin/checkmake Makefile
	make -C node-red test
	make -C controller test
	make -C segmenter test
	make -C os test
	make -C documentation test

developer-mode:
	git remote set-url origin git@github.com:PlanktoScope/PlanktoScope.git
	git fetch origin

# consider using just instead of make https://github.com/casey/just
