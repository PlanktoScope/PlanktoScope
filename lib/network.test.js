import { describe, test, before, after } from "node:test"
import { readFile } from "node:fs/promises"

import { NetworkManager } from "./network.js"

let networkmanager = null

before(async () => {
  networkmanager = new NetworkManager()
  await networkmanager.init()
})

test("scan", async () => {
  await networkmanager.scan()
})

describe("getWifis", async () => {
  test("returns PlanktoScope own wifi", async (t) => {
    const machine_name = await readFile("/var/run/machine-name", "utf8")

    const wifis = await networkmanager.getWifis()
    const wifi = wifis.find(
      (wifi) => wifi.ssid == `PlanktoScope ${machine_name}`,
    )
    t.assert.ok(wifi)
  })
})

after(async () => {
  await networkmanager.deinit()
  networkmanager = null
})
