.PHONY: all clean setup test
.DEFAULT_GOAL := setup

setup:
	poetry lock && poetry install --with=dev
	sudo cp ../os/planktoscope-app-env/python-hardware-controller/etc/systemd/system/planktoscope-org.controller.service /etc/systemd/system/planktoscope-org.controller.service
	sudo systemctl daemon-reload

test:
	~/go/bin/checkmake Makefile
	poetry run poe check
