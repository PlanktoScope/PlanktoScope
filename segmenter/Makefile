.PHONY: all clean setup test
.DEFAULT_GOAL := setup

setup:
	poetry lock && poetry install --with=dev

test:
	~/go/bin/checkmake Makefile
	poetry run poe check
