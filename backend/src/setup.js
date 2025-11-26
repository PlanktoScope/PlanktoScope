// This file is related to setting up the PlanktoScope
// setup refers to configuration done at first start by the user

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

import { procedure } from "../../lib/mqtt.js"
import { updateSoftwareConfig } from "../../lib/file-config.js"
import { promiseDashboardOnline } from "../../lib/nodered.js"

import { has_eeprom_hardware_version } from "./factory.js"

await procedure("setup/read", async () => {
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
await procedure("setup/update", async (data) => {
  const { country, timezone, hardware_version } = Schema.parse(data)

  // await setWifiRegulatoryDomain(country)
  // await setTimezone(timezone)
  // await (hardware_version && setHardwareVersion(hardware_version))

  await Promise.all([
    setWifiRegulatoryDomain(country),
    setTimezone(timezone),
    hardware_version && setHardwareVersion(hardware_version),
  ])

  await updateSoftwareConfig({ user_setup: true })

  await promiseDashboardOnline()
})
