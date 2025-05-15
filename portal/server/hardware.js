import { readFile, writeFile } from "fs/promises";

export const hardware_versions = ["v3.0", "v2.6", "v2.5", "v2.3", "v2.1"].map(
  (v) => {
    return { label: `PlanktoScope ${v}`, value: `PlanktoScope ${v}` };
  }
);

const path = "/home/pi/PlanktoScope/config.json";

export async function getHardwareVersion() {
  let data;

  try {
    data = await readFile(path, { encoding: "utf8" });
  } catch (err) {
    if (err.code !== "ENOENT") throw err;
  }

  let config = {};

  try {
    config = JSON.parse(data);
  } catch {}

  return config.acq_instrument || null;
}

export async function setHardwareVersion() {}
