#!/bin/bash -euxo pipefail
# The MQTT broker provides a common message broker for PlanktoScope applications and acts as the
# entrypoint to the Python backend's network API.
# Eventually, the scope of responsibilities of the MQTT broker may be reduced, with various
# responsibilities shifted to more standard network API mechanisms such as RESTful HTTP APIs.

# Install the Mosquitto MQTT broker and command-line clients
# TODO: install the mosquitto server as a Pallet package instead
sudo apt-get update -y
sudo apt-get install -y mosquitto mosquitto-clients
