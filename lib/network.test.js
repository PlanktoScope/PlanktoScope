import { describe, test, before, after } from "node:test"
import { NetworkManager } from "./network.js"

let networkmanager = null
// const service = "mediamtx"

before(async () => {
  networkmanager = new NetworkManager()
  await networkmanager.init()
})

test("scan", async () => {
  await networkmanager.scan()
})

describe("getWifis", async () => {
  test("returns PlanktoScope own wifi", async (t) => {
    const wifis = await networkmanager.getWifis()
    const wifi = wifis.find((wifi) => wifi.ssid == "PlanktoScope fork-wave")
    t.assert.ok(wifi)
  })
})

after(async () => {
  await networkmanager.deinit()
  networkmanager = null
})
