import { read as readEEPROM, write as writeEEPROM } from "./eeptools.js"
import { Chip, Line } from "node-libgpiod"

async function write(data) {
  const chip = new Chip(0)
  const eeprom_rp = new Line(chip, 26)
  eeprom_rp.requestOutputMode()
  eeprom_rp.setValue(0)

  data.custom_data = [
    Buffer.from(JSON.stringify(data.custom_data)).toString("base64"),
  ]

  try {
    await writeEEPROM(data)
  } finally {
    eeprom_rp.setValue(1)
    eeprom_rp.release()
  }
}

async function read() {
  const data = await readEEPROM()
  data.custom_data = JSON.parse(
    Buffer.from(data.custom_data[0], "base64").toString()
  )
  return data
}

const foo = await read()
console.log(foo)

foo.custom_data = { super: "cool", date: Date.now() }

await write(foo)

console.log(await read())
