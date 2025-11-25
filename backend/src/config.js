import { publish, procedure } from "../../lib/mqtt.js"

import {
  connectToWifi,
  DeviceWireless,
  getWifis,
  scan,
} from "../../lib/network.js"

async function publishAccessPoints() {
  try {
    const wifis = await getWifis()
    publish("config/wifis", wifis, null, { retain: true })
  } catch (err) {
    console.error(err)
  }
}

DeviceWireless.on("AccessPointAdded", (/*access_point*/) => {
  publishAccessPoints()
})

DeviceWireless.on("AccessPointRemoved", (/*access_point*/) => {
  publishAccessPoints()
})

await procedure("config/wifis/scan", async () => {
  await scan()
})

await procedure("config/wifis/connect", async (data) => {
  await connectToWifi(data.path)
})
;(async () => {
  await publishAccessPoints()
  await scan()
  await publishAccessPoints()
})()
