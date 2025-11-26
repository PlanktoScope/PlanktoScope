// This file is related to setting up the PlanktoScope
// setup refers to configuration done at first start by the user

import * as z from "zod"

import {
  setHardwareVersion,
  detectHardwareVersion,
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

await procedure("setup/read", async () => {
  const [countries, country, timezones, timezone] = await Promise.all([
    getWifiRegulatoryDomains(),
    getWifiRegulatoryDomain(),
    getTimezones(),
    getTimezone(),
  ])

  return {
    countries,
    country,
    timezones,
    timezone,
  }
})

const Schema = z.object({
  country: z.string(),
  timezone: z.string(),
})
await procedure("setup/update", async (data) => {
  const { country, timezone } = Schema.parse(data)

  const hardware_version = await detectHardwareVersion()

  await Promise.all([
    setWifiRegulatoryDomain(country),
    setTimezone(timezone),
    setHardwareVersion(hardware_version),
  ])

  await updateSoftwareConfig({ user_setup: true })

  await promiseDashboardOnline()
})
