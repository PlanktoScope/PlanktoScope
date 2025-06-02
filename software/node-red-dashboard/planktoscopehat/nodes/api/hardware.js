import { readFile, copyFile } from "fs/promises"

const hardware_versions = ["v3.0", "v2.6", "v2.5", "v2.3", "v2.1"].map((v) => {
  return { label: `PlanktoScope ${v}`, value: v }
})

export async function getHardwareVersions() {
  return { hardware_versions }
}

const path = "/home/pi/PlanktoScope/config.json"

export async function getHardwareVersion() {
  let data

  try {
    data = await readFile(path, { encoding: "utf8" })
  } catch (err) {
    if (err.code !== "ENOENT") throw err
  }

  let config = {}

  try {
    config = JSON.parse(data)
  } catch {
    /* empty */
  }

  return config.acq_instrument.split(" ")[1] || null
}

export async function setHardwareVersion(hardware_version) {
  await Promise.all([
    copyFile(
      `/home/pi/PlanktoScope/software/node-red-dashboard/default-configs/${hardware_version}.config.json`,
      "/home/pi/PlanktoScope/config.json"
    ),
    copyFile(
      `/home/pi/PlanktoScope/device-backend/default-configs/${hardware_version}.hardware.json`,
      "/home/pi/PlanktoScope/hardware.json"
    ),
  ])
  // TODO: confgure node-red
  // TODO: restart backend
}
