.PHONY: setup
.DEFAULT_GOAL := setup

setup:
	cd controller && poetry lock && poetry install --with=dev
	cd segmenter && poetry lock && poetry install --with=dev
	cd node-red && npm install
	cd node-red/nodes && npm install
	cd documentation && poetry lock && poetry install
