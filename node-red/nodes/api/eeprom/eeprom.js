import { read as readEEPROM, write as writeEEPROM } from "./eeptools.js"
import { Chip, Line } from "node-libgpiod"

const type = "24c32"
const address = "50"
const gpio_write_protect = 26

export async function write(data) {
  const chip = new Chip(0)
  const line = new Line(chip, gpio_write_protect)
  line.requestOutputMode()
  line.setValue(0)

  data = structuredClone(data)
  if (data.custom_data) {
    data.custom_data = [
      Buffer.from(JSON.stringify(data.custom_data), "utf8").toString("base64"),
    ]
  }

  try {
    await writeEEPROM({ type, address }, data)
  } finally {
    line.setValue(1)
    line.release()
  }
}

export async function read() {
  const data = await readEEPROM({ type, address })

  if (data.custom_data?.[0]) {
    data.custom_data = JSON.parse(
      Buffer.from(data.custom_data[0], "base64").toString("utf8")
    )
  }

  return data
}

// const eeprom = {
//   product_uuid: "167fe1a8-62aa-41d3-a746-8b67d8342f4c",
//   product_id: "0x0000",
//   product_ver: "0x0000",
//   vendor: "FairScope",
//   product: "PlanktoScope v3",
//   dt_blob: "planktoscope-hat",
// }
// await write(eeprom)

// do {
//   const eeprom = await read()
//   eeprom.custom_data = {
//     random: Math.random().toString().split("0.")[1],
//     utf8: "@#$@RD)@@² ³’¥²³Ü‘~🤣",
//   }
//   await write(eeprom)
//   console.log(await read())
// } while (true)
