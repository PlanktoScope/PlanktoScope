.PHONY: controller setup
.DEFAULT_GOAL := setup

controller:
	cd controller && poetry lock && poetry install --with=dev
	sudo cp os/planktoscope-app-env/python-hardware-controller/etc/systemd/system/planktoscope-org.controller.service /etc/systemd/system/planktoscope-org.controller.service
	sudo systemctl daemon-reload

setup: controller
	cd segmenter && poetry lock && poetry install --with=dev
	cd node-red && npm install
	cd node-red/nodes && npm install
	cd documentation && poetry lock && poetry install
