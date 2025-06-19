.PHONY: all clean
.DEFAULT_GOAL := setup

.PHONY: setup
setup:
	sudo apt install golang --no-install-recommends
	go install github.com/mrtazz/checkmake/cmd/checkmake@latest
	git submodule update --init
	make -C node-red setup
	make -C controller setup
	make -C segmenter setup
	make -C os setup
	make -C documentation setup

.PHONY: test
test:
	~/go/bin/checkmake Makefile
	make -C node-red test
	make -C controller test
	make -C segmenter test
	make -C os test
	make -C documentation test

.PHONY: developer-mode
developer-mode:
	git remote set-url origin git@github.com:PlanktoScope/PlanktoScope.git
	git fetch origin

# consider using just instead of make https://github.com/casey/just
