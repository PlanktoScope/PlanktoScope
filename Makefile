.PHONY: main controller setup dev test test-node-red
.DEFAULT_GOAL := setup

setup-main:
	git submodule update --init

setup-controller:
	cd controller && poetry lock && poetry install --with=dev
	sudo cp os/planktoscope-app-env/python-hardware-controller/etc/systemd/system/planktoscope-org.controller.service /etc/systemd/system/planktoscope-org.controller.service
	sudo systemctl daemon-reload

setup: main controller
	cd segmenter && poetry lock && poetry install --with=dev
	cd node-red && npm install
	cd node-red/nodes && npm install
	cd documentation && poetry lock && poetry install

developer-mode:
	git remote set-url origin git@github.com:PlanktoScope/PlanktoScope.git
	git fetch origin

test: test-node-red
	cd controller && poetry run poe check
	cd segmenter && poetry run poe check
# cd documentation && poetry run poe check

test-node-red:
	jq . node-red/projects/adafruithat/flows.json 1> /dev/null
	jq . node-red/projects/planktoscopehat/flows.json 1> /dev/null
	jq . node-red/projects/dashboard/flows.json 1> /dev/null
	cd node-red/nodes && npm test
# Too many errors for now
# cd node-red && npx nrlint projects/adafruithat/flows.json
# cd node-red && npx nrlint projects/planktoscopehat/flows.json
# cd node-red && npx nrlint projects/dashboard/flows.json
