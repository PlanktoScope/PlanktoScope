import { publish, procedure } from "../../../lib/mqtt.js"

import { NetworkManager } from "../../../lib/network.js"

const networkmanager = new NetworkManager()
await networkmanager.init()

async function publishAccessPoints() {
  try {
    const wifis = await networkmanager.getWifis()
    publish("network/wifi/list", wifis, null, { retain: true })
  } catch (err) {
    console.error(err)
  }
}

await networkmanager.DeviceWireless.subscribe(
  "AccessPointAdded",
  (/*access_point*/) => {
    publishAccessPoints()
  },
)

await networkmanager.DeviceWireless.subscribe(
  "AccessPointRemoved",
  (/*access_point*/) => {
    publishAccessPoints()
  },
)

await procedure("network/wifi/scan", async () => {
  await networkmanager.scan()
})

await procedure("network/wifi/connect", async (data) => {
  await networkmanager.connectToWifi(data.path)
})

//
;(async () => {
  await publishAccessPoints()
  await networkmanager.scan()
  await publishAccessPoints()
})()
