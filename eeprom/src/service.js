import crypto from "node:crypto"
import * as z from "zod"

import mqtt from "mqtt"

import { read, write } from "./eeprom.js"
import {
  hasHardwareVersion,
  setHardwareVersion,
  getHardwareVersions,
  getHardwareVersion,
} from "../../node-red/nodes/api/hardware.js"
import {
  getWifiRegulatoryDomains,
  setWifiRegulatoryDomain,
  getWifiRegulatoryDomain,
} from "../../node-red/nodes/api/country.js"
import {
  getTimezones,
  getTimezone,
  setTimezone,
} from "../../node-red/nodes/api/timezone.js"
import { readFile } from "node:fs/promises"

process.title = "planktoscope-org.eeprom"

const client = mqtt.connect("ws://pkscope-wax-ornament-42816:9001", {
  protocolVersion: 5,
  properties: {
    requestResponseInformation: true,
  },
})

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

const handlers = new Map()

async function handle(topic, handler) {
  await client.subscribeAsync(topic)
  handlers.set(topic, handler)
}

client.on("message", async (topic, message, packet) => {
  const handler = handlers.get(topic)
  if (!handler) return

  const responseTopic = packet.properties?.responseTopic
  if (!responseTopic) return

  async function respond(data) {
    await client.publishAsync(responseTopic, JSON.stringify(data))
  }

  let data
  if (message.length > 0) {
    try {
      data = JSON.parse(message.toString())
    } catch (err) {
      await respond({ error: err.message })
      return
    }
  }

  let result
  try {
    result = await handler(data)
  } catch (err) {
    console.error(err)

    if (err instanceof z.ZodError) {
      await respond({
        error: { message: "Validation error", data: err.issues },
      })
    } else {
      await respond({ error: { message: err.message } })
    }
    return
  }

  await respond({ result })
})

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

client.on("message", (topic, message, packet) => {
  console.debug("mqtt message", { topic, message, packet })
})

client.on("error", (err) => {
  console.error("mqtt error", err)
})

client.on("connect", (packet) => {
  console.debug("mqtt connect", packet)
})

client.on("disconnect", () => {
  console.debug("mqtt disconnect")
})

client.on("offline", () => {
  console.debug("mqtt offline")
})

client.on("reconnect", () => {
  console.debug("mqtt reconnect")
})
