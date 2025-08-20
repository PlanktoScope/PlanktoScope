import { Chip, Line } from "node-libgpiod"
import child_process from "node:child_process"

import i2c from "i2c-bus"

import { read as readEEPROM, write as writeEEPROM } from "./eeptools.js"

const type = "24c32"
const address = "50"
const gpio_write_protect = 26

export function isSupported() {
  let supported = false

  try {
    child_process.execFileSync("sudo", [
      "dtoverlay",
      "i2c-gpio",
      "i2c_gpio_sda=0",
      "i2c_gpio_scl=1",
      "bus=9",
    ])
    const i2c1 = i2c.openSync(9)
    supported = i2c1.scanSync().includes("80")
  } catch {
    //
  }

  return supported
}

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

// Make sure we run only one at a time
const queue = []
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
