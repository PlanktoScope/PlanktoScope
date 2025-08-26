import * as z from "zod"

import {
  setHardwareVersion,
  getHardwareVersions,
  getHardwareVersion,
} from "../../lib/hardware.js"
import {
  getWifiRegulatoryDomains,
  setWifiRegulatoryDomain,
  getWifiRegulatoryDomain,
} from "../../lib/country.js"
import { getTimezones, getTimezone, setTimezone } from "../../lib/timezone.js"

import { handle } from "../../lib/mqtt.js"
import {
  readSoftwareConfig,
  updateSoftwareConfig,
} from "../../lib/file-config.js"
import { getActiveNodeRedProject } from "../../lib/nodered.js"

import { has_eeprom_hardware_version } from "./bootstrap.js"

// const setup_init_schema = z.object({
//   origin: z.url(),
// })
await handle("setup/init", async (data) => {
  // data = setup_init_schema.parse(data)
  const { origin } = data

  const software_config = await readSoftwareConfig()

  if (!software_config) {
    return {
      redirect: new URL("/setup", origin),
    }
  }

  if (!software_config.user_setup) {
    return {
      redirect: new URL("/setup", origin),
    }
  }

  const node_red_project = await getActiveNodeRedProject()
  const url = new URL(origin)
  url.port = 80
  url.pathname =
    node_red_project === "dashboard"
      ? "/ps/node-red-v2/dashboard"
      : "/ps/node-red-v2/ui"

  return { redirect: url }
})

await handle("setup/read", async () => {
  const [
    countries,
    country,
    timezones,
    timezone,
    hardware_versions,
    hardware_version,
  ] = await Promise.all([
    getWifiRegulatoryDomains(),
    getWifiRegulatoryDomain(),
    getTimezones(),
    getTimezone(),
    has_eeprom_hardware_version ? null : getHardwareVersions(),
    has_eeprom_hardware_version ? null : getHardwareVersion(),
  ])

  return {
    countries,
    country,
    timezones,
    timezone,
    hardware_versions,
    hardware_version,
  }
})

const Schema = z.object({
  country: z.string(),
  timezone: z.string(),
  hardware_version: z.string().optional(),
})
await handle("setup/update", async (data) => {
  const { country, timezone, hardware_version } = Schema.parse(data)

  await Promise.all([
    setWifiRegulatoryDomain(country),
    setTimezone(timezone),
    hardware_version && setHardwareVersion(hardware_version),
  ])

  await updateSoftwareConfig({ user_setup: true })
})
