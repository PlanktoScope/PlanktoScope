// https://nodered.org/docs/user-guide/runtime/configuration

const yaml = require("js-yaml");
const fs = require("fs");

const installer_config = yaml.load(
	fs.readFileSync("/usr/share/planktoscope/installer-config.yml", "utf8"),
);

const config = require(	`./${installer_config.hardware}/settings.js`);

module.exports = config;
