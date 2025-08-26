import { writeFile } from "fs/promises"
import { readFile, access, constants, copyFile } from "fs/promises"

const HARDWARE_PATH = "/home/pi/PlanktoScope/hardware.json"
const SOFTWARE_PATH = "/home/pi/PlanktoScope/config.json"

async function hasConfig(path) {
  try {
    await access(path, constants.R_OK)
    return true
  } catch {
    return false
  }
}

export async function initConfigFiles(hardware_version) {
  await Promise.all([
    copyFile(
      `/home/pi/PlanktoScope/default-configs/${hardware_version}.config.json`,
      "/home/pi/PlanktoScope/config.json",
    ),
    copyFile(
      `/home/pi/PlanktoScope/default-configs/${hardware_version}.hardware.json`,
      "/home/pi/PlanktoScope/hardware.json",
    ),
  ])
}

async function updateConfig(path, values) {
  const config = await readConfig(path)
  if (!config) {
    throw new Error(`Cannot update missing config ${path}`)
  }

  Object.assign(config, values)

  await writeFile(path, JSON.stringify(config, null, 2))
}

async function readConfig(path) {
  let data

  try {
    data = await readFile(path, { encoding: "utf8" })
  } catch (err) {
    if (err.code === "ENOENT") return null
    throw err
  }

  return JSON.parse(data)
}

export async function hasSoftwareConfig(...args) {
  return hasConfig(SOFTWARE_PATH, ...args)
}

export async function hasHardwareConfig(...args) {
  return hasConfig(HARDWARE_PATH, ...args)
}

export async function updateSoftwareConfig(...args) {
  return updateConfig(SOFTWARE_PATH, ...args)
}

export async function updateHardwareConfig(...args) {
  return updateConfig(HARDWARE_PATH, ...args)
}

export async function readSoftwareConfig(...args) {
  return readConfig(SOFTWARE_PATH, ...args)
}

export async function readHardwareConfig(...args) {
  return readConfig(HARDWARE_PATH, ...args)
}
