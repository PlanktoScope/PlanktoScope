.PHONY: all clean setup test
.DEFAULT_GOAL := setup

setup:
	poetry lock && poetry install

test:
	checkmake Makefile
	poetry run poe check
