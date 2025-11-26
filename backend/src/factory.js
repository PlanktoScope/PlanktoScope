// This file is related to factory setup of the PlanktoScope
// factory setup refers to configuration done at runtime or by FairScope
// without involvment of the users
// For example updating the EEPROM

import crypto from "node:crypto"
// import * as z from "zod"

import { read, write } from "../../lib/eeprom.js"
import { setHardwareVersion } from "../../lib/hardware.js"

import { procedure, request } from "../../lib/mqtt.js"
import { hasSoftwareConfig } from "../../lib/file-config.js"

await procedure("factory/init", async () => {
  const eeprom = await read()

  if (eeprom?.custom_data?.eeprom_version !== 0) {
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
        hardware_version: "", // TODO
        eeprom_version: 0,
        led_operating_time: 0,
      },
    }
  }

  return eeprom
})

await procedure("factory/update", async (data) => {
  await write(data)

  await request("light", { action: "off" })
  await request("light", { action: "save" })

  await request("actuator/bubbler", { action: "off" })
  await request("actuator/bubbler", { action: "save" })
})
;(async () => {
  let eeprom

  try {
    // If the PlanktoScope has an EEPROM with the hardware version set
    // configure the PlanktoScope with that so we don't need to ask users for it
    eeprom = await read()
    // eslint-disable-next-line no-empty
  } catch {}
  const hardware_version = eeprom?.custom_data?.hardware_version
  if (hardware_version && !(await hasSoftwareConfig())) {
    await setHardwareVersion(hardware_version)
  }
})()
