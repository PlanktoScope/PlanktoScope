// This file is related to bootstraping the PlanktoScope
// bootstrap refers to configuration done at runtime or by FairScope
// without involvment of the users
// For example updating the EEPROM

import crypto from "node:crypto"
// import * as z from "zod"

import { read, write } from "../../lib/eeprom.js"
import { setHardwareVersion } from "../../lib/hardware.js"

import { procedure, request } from "../../lib/mqtt.js"
import { hasSoftwareConfig } from "../../lib/file-config.js"

// If the PlanktoScope has an EEPROM with the hardware version set
// configure the PlanktoScope with that so we don't need to ask users for it
let cached
try {
  cached = await read()
} catch (err) {
  console.debug(err)
}

const hardware_version = cached?.custom_data?.hardware_version
if (hardware_version && !(await hasSoftwareConfig())) {
  await setHardwareVersion(hardware_version)
}

export const has_eeprom_hardware_version = !!hardware_version

await procedure("bootstrap/init", async () => {
  const eeprom = cached

  if (eeprom?.custom_data?.eeprom_version !== "0") {
    // await request("light", { action: "on" })

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

await procedure("bootstrap/update", async (data) => {
  await write(data)

  // await request("light", { action: "off" })
  // await request("light", { action: "save" })

  cached = await read()
})

await procedure("bootstrap/read", async () => {
  return cached
})
