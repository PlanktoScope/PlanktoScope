import { read as readEEPROM, write as writeEEPROM } from "./eeptools.js"
import { Chip, Line } from "node-libgpiod"

import { randomBytes } from "crypto"

const type = "24c32"
const address = "50"
const gpio_write_protect = 26

async function write(data) {
  const chip = new Chip(0)
  const line = new Line(chip, gpio_write_protect)
  line.requestOutputMode()
  line.setValue(0)

  if (data.custom_data) {
    data.custom_data = [JSON.stringify(data.custom_data, null, 2)]
  }

  try {
    await writeEEPROM({ type, address }, data)
  } finally {
    line.setValue(1)
    line.release()
  }
}

async function read() {
  const data = await readEEPROM({ type, address })

  if (data.custom_data?.[0]) {
    data.custom_data = JSON.parse(data.custom_data[0])
  }

  return data
}

const eeprom = {
  product_uuid: "167fe1a8-62aa-41d3-a746-8b67d8342f4c",
  product_id: "0x0000",
  product_ver: "0x0000",
  vendor: "FairScope",
  product: "PlanktoScope v3",
  dt_blob: "planktoscope-hat",
}
await write(eeprom)

do {
  const eeprom = await read()
  eeprom.custom_data = {
    random: Math.random().toString().split("0.")[1],
    latin1: randomBytes(2048).toString("base64"),
  }
  console.log("writing", '"', eeprom.custom_data.latin1, '"')
  // console.log(randomBytes(128).toString("latin1"))
  await write(eeprom)
  console.log(await read())
} while (true)
