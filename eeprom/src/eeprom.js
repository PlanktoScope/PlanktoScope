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

  console.debug("eeprom", "writing", data)

  try {
    await writeEEPROM({ type, address }, data)
  } finally {
    line.setValue(1)
    line.release()
  }
}

// Make sure we run only one at a time
let queue = []
let running = false

export function read() {
  const promise = Promise.withResolvers()
  queue.push(promise)

  if (!running) {
    _read()
      .then((result) => {
        while (queue.length > 0) {
          const next = queue.shift()
          next.resolve(result)
        }
      })
      .catch((error) => {
        while (queue.length > 0) {
          const next = queue.shift()
          next.reject(error)
        }
      })
      .finally(() => {
        running = false
      })
    running = true
  }

  return promise.promise
}

async function _read() {
  const data = await readEEPROM({ type, address })

  if (data.custom_data?.[0]) {
    data.custom_data = JSON.parse(
      Buffer.from(data.custom_data[0], "base64").toString("utf8"),
    )
  }

  return data
}
