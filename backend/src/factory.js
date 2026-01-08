// This file is related to factory setup of the PlanktoScope
// factory setup refers to configuration done at runtime or by FairScope
// without involvment of the users
// For example updating the EEPROM

import crypto from "node:crypto"
import * as z from "zod"

import { read, write } from "../../lib/eeprom.js"
import { procedure, request } from "../../lib/mqtt.js"
import { hardware_versions, setHardwareVersion } from "../../lib/hardware.js"

await procedure("factory/init", async () => {
  let eeprom = await read()

  if (eeprom?.custom_data?.eeprom_version !== 0) {
    eeprom = {
      product_uuid: crypto.randomUUID(),
      product_id: "0x0000", // TODO
      product_ver: "0x0000", //TODO
      vendor: "FairScope",
      product: "PlanktoScope HAT v3",
      current_supply: 0,
      dt_blob: "planktoscope-hat-v3",
      custom_data: {
        serial_number: "",
        hardware_version: "v3.0",
        eeprom_version: 0,
        led_operating_time: 0,
      },
    }
  }

  return { eeprom, hardware_versions }
})

const Schema = z.object({
  hardware_version: z.enum(hardware_versions),
})

await procedure("factory/update", async (data) => {
  const { hardware_version } = Schema.parse(data)

  await Promise.all([
    hardware_version === "v3.0" && write(data),
    setHardwareVersion(hardware_version),
  ])

  if (hardware_version === "v3.0") {
    await request("light", { action: "off" })
    await request("light", { action: "save" })

    await request("actuator/bubbler", { action: "off" })
    await request("actuator/bubbler", { action: "save" })
  }
})
