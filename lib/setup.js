import * as z from "zod"

import { publish } from "./mqtt.js"
import { setHardwareVersion, detectHardwareVersion } from "./hardware.js"
import {
  getWifiRegulatoryDomains,
  setWifiRegulatoryDomain,
  getWifiRegulatoryDomain,
} from "./country.js"
import { getTimezones, getTimezone, setTimezone } from "./timezone.js"

import { updateSoftwareConfig } from "./file-config.js"
import { promiseDashboardOnline } from "./nodered.js"

export async function readSetup() {
  const [regions, region, timezones, timezone] = await Promise.all([
    getWifiRegulatoryDomains(),
    getWifiRegulatoryDomain(),
    getTimezones(),
    getTimezone(),
  ])

  return {
    regions,
    region,
    timezones,
    timezone,
  }
}

const Schema = z.object({
  region: z.string(),
  timezone: z.string(),
})

export async function writeSetup(data) {
  const { region, timezone } = Schema.parse(data)
  const hardware_version = await detectHardwareVersion()

  await Promise.all([
    setWifiRegulatoryDomain(region),
    setTimezone(timezone),
    setHardwareVersion(hardware_version),
  ])

  await Promise.all([
    updateSoftwareConfig({ user_setup: true }),
    promiseDashboardOnline(),
  ])

  await publish("setup/ready", {})
}
