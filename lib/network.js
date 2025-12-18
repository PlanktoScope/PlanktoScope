/* eslint-disable n/no-top-level-await */

import { systemBus } from "dbus.js"

export class NetworkManager {
  system_bus = null
  network_manager = null
  service = null

  async init() {
    if (this.network_manager) return

    const system_bus = systemBus()
    const service = system_bus.getService("org.freedesktop.NetworkManager")

    const network_manager = await service.getInterface(
      "/org/freedesktop/NetworkManager",
      "org.freedesktop.NetworkManager",
    )

    const [device_path] = await network_manager.GetDeviceByIpIface("wlan0")
    const [DeviceWireless, DeviceWireless_Properties] = await Promise.all([
      service.getInterface(
        device_path,
        "org.freedesktop.NetworkManager.Device.Wireless",
      ),
      service.getInterface(device_path, "org.freedesktop.DBus.Properties"),
    ])

    Object.assign(this, {
      system_bus,
      service,
      network_manager,
      device_path,
      DeviceWireless,
      DeviceWireless_Properties,
    })
  }

  // TODO: real async
  async deinit() {
    this.system_bus?.connection.end()
    this.system_bus = null
    this.network_manager = null
    this.service.bus.connection.end()
    this.service = null
  }

  async scan() {
    const deferred = Promise.withResolvers()

    // > To know when the scan is finished, use the "PropertiesChanged" signal from "org.freedesktop.DBus.Properties" to listen to changes to the "LastScan" property.
    // https://networkmanager.dev/docs/api/latest/gdbus-org.freedesktop.NetworkManager.Device.Wireless.html#gdbus-method-org-freedesktop-NetworkManager-Device-Wireless.RequestScan
    function handler(interface_name, changed_properties) {
      if (interface_name !== "org.freedesktop.NetworkManager.Device.Wireless") {
        return
      }

      const LastScan = changed_properties.find((changed_property) => {
        const [property_name] = changed_property
        return property_name === "LastScan"
      })
      if (!LastScan) return

      this.DeviceWireless_Properties.unsubscribe(
        "PropertiesChanged",
        handler,
      ).then(deferred.resolve, deferred.reject)
    }
    await this.DeviceWireless_Properties.subscribe("PropertiesChanged", handler)

    await this.DeviceWireless.RequestScan({})

    return deferred.promise
  }

  async getWifis() {
    const [access_point_paths] = await this.DeviceWireless.GetAllAccessPoints()

    const access_points = await Promise.all(
      access_point_paths.map((access_point_path) => {
        return this.service.getInterface(
          access_point_path,
          "org.freedesktop.NetworkManager.AccessPoint",
        )
      }),
    )

    return Promise.all(
      access_points.map(async (access_point) => {
        const [Ssid, frequency, strength] = await Promise.all(
          ["Ssid", "Frequency", "Strength"].map((propName) =>
            readProp(access_point, propName),
          ),
        )
        const ssid = new TextDecoder().decode(Ssid)
        const path = access_point.$parent.name
        return { ssid, frequency, strength, path }
      }),
    )
  }

  async connectToWifi(path) {
    await NetworkManager.AddAndActivateConnection([], this.device_path, path)
  }
}

async function readProp(iface, propName) {
  const bus = iface.$parent.service.bus
  const val = await bus.invoke({
    destination: iface.$parent.service.name,
    path: iface.$parent.name,
    interface: "org.freedesktop.DBus.Properties",
    member: "Get",
    signature: "ss",
    body: [iface.$name, propName],
  })
  return val[0][1][0]
}

if (import.meta.main) {
  const networkmanager = new NetworkManager()
  await networkmanager.init()
  await networkmanager.scan()
  const wifis = await networkmanager.getWifis()
  console.log(wifis)
  await networkmanager.deinit()
}
