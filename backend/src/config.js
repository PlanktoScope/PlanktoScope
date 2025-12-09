import { publish, procedure } from "../../lib/mqtt.js"

import { NetworkManager } from "../../lib/network.js"

const networkmanager = new NetworkManager()
await networkmanager.init()

async function publishAccessPoints() {
  try {
    const wifis = await networkmanager.getWifis()
    publish("config/wifis", wifis, null, { retain: true })
  } catch (err) {
    console.error(err)
  }
}

networkmanager.DeviceWireless.on("AccessPointAdded", (/*access_point*/) => {
  publishAccessPoints()
})

networkmanager.DeviceWireless.on("AccessPointRemoved", (/*access_point*/) => {
  publishAccessPoints()
})

await procedure("config/wifis/scan", async () => {
  await networkmanager.scan()
})

await procedure("config/wifis/connect", async (data) => {
  await networkmanager.connectToWifi(data.path)
})
;(async () => {
  await publishAccessPoints()
  await networkmanager.scan()
  await publishAccessPoints()
})()
