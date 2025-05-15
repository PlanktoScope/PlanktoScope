import express from "express";
import cors from "cors";

import {
  getWifiRegulatoryDomain,
  setWifiRegulatoryDomain,
  countries,
} from "./country.js";

import {
  setHardwareVersion,
  getHardwareVersion,
  hardware_versions,
} from "./hardware.js";

import { setTimezone, getTimezone, timezones } from "./timezone.js";
import { getName, getHostname } from "./identity.js";

const app = express();

app.use(cors());
app.use(express.json());

app.get("/hardware-versions", (req, res) => {
  res.json(hardware_versions);
});

app.get("/hardware", async (req, res) => {
  const value = await getHardwareVersion();
  res.json({ value });
});

app.post("/hardware", async (req, res) => {
  await setHardwareVersion(req.body.value);
  res.end();
});

app.get("/countries", (req, res) => {
  res.json(countries);
});

app.get("/country", async (req, res) => {
  const value = await getWifiRegulatoryDomain();
  res.json({ value });
});

app.post("/country", async (req, res) => {
  await setWifiRegulatoryDomain(req.body.value);
  res.end();
});

app.get("/timezones", (req, res) => {
  res.json(timezones);
});

app.get("/timezone", async (req, res) => {
  const value = await getTimezone();
  res.json({ value });
});

app.post("/timezone", async (req, res) => {
  await setTimezone(req.body.value);
  res.end();
});

app.get("/bootstrap", async (req, res) => {
  const [hardware_version, name, hostname] = await Promise.all([
    getHardwareVersion(),
    getName(),
    getHostname(),
  ]);
  const access_hostname = req.hostname;

  res.json({
    setup: !hardware_version,
    name,
    hostname,
    access_hostname,
  });
});

app.listen(8585);
