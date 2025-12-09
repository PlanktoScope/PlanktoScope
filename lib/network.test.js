import { describe, afterEach, test, before, after } from "node:test"
// import { Systemctl } from "./systemctl.js"
import { getWifis, scan } from "./network.js"

// let systemctl = null
// const service = "mediamtx"

// before(async () => {
//   systemctl = new Systemctl()
//   await systemctl.init()
// })

// Prevents "service start request repeated too quickly, refusing to start"
// and the likes - https://serverfault.com/questions/845471/service-start-request-repeated-too-quickly-refusing-to-start-limit
// afterEach(async () => {
//   await systemctl.reload()
// })

test("scan", async () => {
  await scan()
})

describe("getWifis", async () => {
  test("returns PlanktoScope own wifi", async (t) => {
    const wifis = await getWifis()
    console.log(wifis)
    const wifi = wifis.find((wifi) => wifi.ssid == "PlanktoScope fork-wave")
    t.assert.ok(wifi)
  })
})

// after(async () => {
//   await systemctl.deinit()
//   systemctl = null
// })
