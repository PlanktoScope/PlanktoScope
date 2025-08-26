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
    getHardwareVersions(),
    getHardwareVersion(),
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
  hardware_version: z.string(),
})
await handle("setup/update", async (data) => {
  const { country, timezone, hardware_version } = Schema.parse(data)

  await Promise.all([
    setWifiRegulatoryDomain(country),
    setTimezone(timezone),
    setHardwareVersion(hardware_version),
  ])
})
