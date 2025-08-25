import crypto from "node:crypto"
import * as z from "zod"

import { read, write } from "./eeprom.js"
import {
  hasHardwareVersion,
  setHardwareVersion,
  getHardwareVersions,
  getHardwareVersion,
} from "/home/pi/PlanktoScope/lib/hardware.js"
import {
  getWifiRegulatoryDomains,
  setWifiRegulatoryDomain,
  getWifiRegulatoryDomain,
} from "/home/pi/PlanktoScope/lib/country.js"
import {
  getTimezones,
  getTimezone,
  setTimezone,
} from "/home/pi/PlanktoScope/lib/timezone.js"

import { handle } from "/home/pi/PlanktoScope/lib/mqtt.js"

process.title = "planktoscope-org.eeprom"

let cached
try {
  cached = await read()
} catch {
  // ignore
}
const hardware_version = cached?.custom_data?.hardware_version
if (hardware_version && !(await hasHardwareVersion())) {
  await setHardwareVersion(hardware_version)
}

await handle("eeprom/bootstrap", async () => {
  const eeprom = cached

  if (eeprom.custom_data?.eeprom_version !== "0") {
    return {
      product_uuid: crypto.randomUUID(),
      product_id: "0x0000", // TODO
      product_ver: "0x0000", //TODO
      vendor: "FairScope",
      product: "PlanktoScope HAT v3",
      current_supply: 0,
      dt_blob: "planktoscope-hat-v3",
      custom_data: {
        serial_number: "",
        hardware_version: "",
        eeprom_version: 0,
      },
    }
  }

  return eeprom
})

await handle("eeprom/update", async (data) => {
  await write(data)
  cached = await read()
})

await handle("eeprom/read", async () => {
  return cached
})

await handle("first-time-setup/read", async () => {
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
await handle("first-time-setup/update", async (data) => {
  const { country, timezone, hardware_version } = Schema.parse(data)

  await Promise.all([
    setWifiRegulatoryDomain(country),
    setTimezone(timezone),
    setHardwareVersion(hardware_version),
  ])
})
