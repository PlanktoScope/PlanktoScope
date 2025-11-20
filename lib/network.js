import util from "node:util"
import dbus from "@homebridge/dbus-native"
import { pEvent } from "p-event"

const bus = dbus.systemBus()
const service = bus.getService("org.freedesktop.NetworkManager")

const handler = {
  get(target, prop, receiver) {
    // console.log(target, prop, receiver)
    if (prop in target["$methods"]) return util.promisify(target[prop])
    if (prop in target["$properties"]) return util.promisify(target[prop])
    return Reflect.get(...arguments)
  },
}

const original_getInterface = service.getInterface.bind(service)
service.getInterface = function getInterface(...args) {
  return new Promise((resolve, reject) => {
    original_getInterface(...args, (err, int) => {
      if (err) return reject(err)
      if (!int) return resolve(int)
      resolve(new Proxy(int, handler))
    })
  })
}

const NetworkManager = await service.getInterface(
  "/org/freedesktop/NetworkManager",
  "org.freedesktop.NetworkManager",
)

// console.log(NetworkManager)

const device_path = await NetworkManager.GetDeviceByIpIface("wlan0")

const DeviceWireless = await service.getInterface(
  device_path,
  "org.freedesktop.NetworkManager.Device.Wireless",
)
const DeviceWireless_Properties = await service.getInterface(
  device_path,
  "org.freedesktop.DBus.Properties",
)

async function scan() {
  const { promise, resolve } = Promise.withResolvers()

  DeviceWireless_Properties.on(
    "PropertiesChanged",
    (interface_name, changed_properties, invalidated_properties) => {
      if (interface_name !== "org.freedesktop.NetworkManager.Device.Wireless")
        return

      const LastScan = changed_properties.find((changed_property) => {
        const [property_name] = changed_property
        return property_name === "LastScan"
      })

      // FIXME: Remove listener
      if (LastScan) resolve()
    },
  )

  await Promise.all([DeviceWireless.RequestScan({}), promise])
}

// console.log(DeviceWireless)

// DeviceWireless_Properties.on(
//   "PropertiesChanged",
//   (interface_name, changed_properties, invalidated_properties) => {
//     console.log(interface_name, changed_properties, invalidated_properties)
//   },
// )

// DeviceWireless.on("AccessPointAdded", (access_point) => {
//   console.log("AccessPointAdded", access_point)
// })

// DeviceWireless.on("AccessPointRemoved", (access_point) => {
//   console.log("AccessPointRemoved", access_point)
// })

async function getWifis() {
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
      return new TextDecoder().decode(await access_point.Ssid())
    }),
  )
}

await scan()

console.log(await getWifis())

// for (const access_point of access_points) {
//   console.log((await access_point.Ssid()).toString())
// }

console.log("done")
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
