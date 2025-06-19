.PHONY: all clean setup test
.DEFAULT_GOAL := setup

setup:
	sudo apt install jq --no-install-recommends
	npm install
	cd nodes && npm install

test:
	~/go/bin/checkmake Makefile
	jq . projects/adafruithat/flows.json 1> /dev/null
	jq . projects/planktoscopehat/flows.json 1> /dev/null
	jq . projects/dashboard/flows.json 1> /dev/null
	cd nodes && npm test
# Too many errors for now
# cd node-red && npx nrlint projects/adafruithat/flows.json
# cd node-red && npx nrlint projects/planktoscopehat/flows.json
# cd node-red && npx nrlint projects/dashboard/flows.json
