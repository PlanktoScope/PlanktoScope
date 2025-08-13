import { read as readEEPROM, write as writeEEPROM } from "./eeptools.js"
import { Chip, Line } from "node-libgpiod"

async function write(data) {
  const chip = new Chip(0)
  const eeprom_rp = new Line(chip, 26)
  eeprom_rp.requestOutputMode()
  eeprom_rp.setValue(0)

  if (data.custom_data) {
    data.custom_data = [
      Buffer.from(JSON.stringify(data.custom_data, 2), "utf8").toString(
        "latin1"
      ),
    ]
  }

  try {
    await writeEEPROM(data)
  } finally {
    eeprom_rp.setValue(1)
    eeprom_rp.release()
  }
}

async function read() {
  const data = await readEEPROM()

  if (data.custom_data?.[0]) {
    console.log(data.custom_data)
    // try {
    data.custom_data = JSON.parse(
      Buffer.from(data.custom_data[0], "latin1").toString("utf8")
    )
    // } catch {}
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
console.log(await read())

setInterval(async () => {
  const eeprom = await read()
  eeprom.custom_data = { random: Math.random().toString().split("0.")[1] }

  await write(eeprom)
  console.log(await read())
}, 2000)
