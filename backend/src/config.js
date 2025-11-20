import { publish, procedure } from "../../lib/mqtt.js"

import {
  connectToWifi,
  DeviceWireless,
  getWifis,
  scan,
} from "../../lib/network.js"

async function publishAccessPoints() {
  const wifis = await getWifis()
  console.log(wifis)
  publish("config/wifis", wifis, null, { retain: true })
}

DeviceWireless.on("AccessPointAdded", (/*access_point*/) => {
  publishAccessPoints()
})

DeviceWireless.on("AccessPointRemoved", (/*access_point*/) => {
  publishAccessPoints()
})

await procedure("config/wifis/scan", async (data) => {
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

// await procedure("config", async () => {
//   const [
//     countries,
//     country,
//     timezones,
//     timezone,
//     hardware_versions,
//     hardware_version,
//   ] = await Promise.all([
//     getWifiRegulatoryDomains(),
//     getWifiRegulatoryDomain(),
//     getTimezones(),
//     getTimezone(),
//     has_eeprom_hardware_version ? null : getHardwareVersions(),
//     has_eeprom_hardware_version ? null : getHardwareVersion(),
//   ])

//   return {
//     countries,
//     country,
//     timezones,
//     timezone,
//     hardware_versions,
//     hardware_version,
//   }
// })

// const Schema = z.object({
//   country: z.string(),
//   timezone: z.string(),
//   hardware_version: z.string().optional(),
// })
// await procedure("setup/update", async (data) => {
//   const { country, timezone, hardware_version } = Schema.parse(data)

//   await Promise.all([
//     setWifiRegulatoryDomain(country),
//     setTimezone(timezone),
//     hardware_version && setHardwareVersion(hardware_version),
//   ])

//   await updateSoftwareConfig({ user_setup: true })

//   await promiseDashboardOnline()
// })
