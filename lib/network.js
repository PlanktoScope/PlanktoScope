import { pEvent } from "p-event"

import { system_bus } from "./dbus.js"

const service = system_bus.getService("org.freedesktop.NetworkManager")

const NetworkManager = await service.getInterface(
  "/org/freedesktop/NetworkManager",
  "org.freedesktop.NetworkManager",
)

// console.log(NetworkManager)

const device_path = await NetworkManager.GetDeviceByIpIface("wlan0")

export const DeviceWireless = await service.getInterface(
  device_path,
  "org.freedesktop.NetworkManager.Device.Wireless",
)
const DeviceWireless_Properties = await service.getInterface(
  device_path,
  "org.freedesktop.DBus.Properties",
)

export async function scan() {
  await DeviceWireless.RequestScan({})

  // > To know when the scan is finished, use the "PropertiesChanged" signal from "org.freedesktop.DBus.Properties" to listen to changes to the "LastScan" property.
  // https://networkmanager.dev/docs/api/latest/gdbus-org.freedesktop.NetworkManager.Device.Wireless.html#gdbus-method-org-freedesktop-NetworkManager-Device-Wireless.RequestScan
  await pEvent(DeviceWireless_Properties, "PropertiesChanged", {
    multiArgs: true,
    filter: ([
      interface_name,
      changed_properties /*invalidated_properties*/,
    ]) => {
      if (interface_name !== "org.freedesktop.NetworkManager.Device.Wireless")
        return false

      const LastScan = changed_properties.find((changed_property) => {
        const [property_name] = changed_property
        return property_name === "LastScan"
      })

      return !!LastScan
    },
  })
}

export async function getWifis() {
  const access_point_paths = await DeviceWireless.GetAllAccessPoints()

  const access_points = await Promise.all(
    access_point_paths.map((access_point_path) => {
      return service.getInterface(
        access_point_path,
        "org.freedesktop.NetworkManager.AccessPoint",
      )
    }),
  )

  return Promise.all(
    access_points.map(async (access_point) => {
      const ssid = new TextDecoder().decode(await access_point.Ssid())
      const frequency = await access_point.Frequency()
      const strength = await access_point.Strength()
      const path = access_point.$parent.name
      return { ssid, frequency, strength, path }
    }),
  )
}

export async function connectToWifi(path) {
  await NetworkManager.AddAndActivateConnection([], device_path, path)
}

// await scan()

// const wifis = await getWifis()

// const wifi = wifis.find((wifi) => wifi.ssid === "FairScope")

// await NetworkManager.AddAndActivateConnection([], device_path, wifi.path)

// console.log("done")
// process.exit()

// let promise_interf
// function getInterface(service, ...args) {
//   promise_interf ??= new Promise((resolve, reject) => {
//     service.getInterface(...args, (err, result) => {
//       if (err) return reject(err)
//       promise_interf = result
//       resolve(result)
//       // runMethod("Subscribe")
//       //   .then(() => {
//       //     resolve(result)
//       //   })
//       //   .catch((err) => reject(err))
//     })
//   })
//   return promise_interf
// }

// ;("/org/freedesktop/NetworkManager",
//   "org.freedesktop.NetworkManager",
//   async function runMethod(method, ...args) {
//     const interf = await getInterface()
//     console.log(interf)
//     console.log(interf[method])
//     console.log(method)
//     return new Promise((resolve, reject) => {
//       interf[method](...args, (err, ...result) => {
//         if (err) reject(err)
//         else resolve(result)
//       })
//     })
//   })

// const [device_path] = await runMethod("GetDeviceByIpIface", "wlan0")

// const device = getInterface()()

// console.log(devices)
