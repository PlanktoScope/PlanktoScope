import util from "node:util"
import dbus from "@homebridge/dbus-native"

let system_bus

try {
  system_bus = dbus.systemBus()
} catch {}

export { system_bus }

const handler = {
  get(target, prop, _receiver) {
    // console.log(target, prop, receiver)
    if (prop in target["$methods"]) return util.promisify(target[prop])
    if (prop in target["$properties"]) return util.promisify(target[prop])
    return Reflect.get(...arguments)
  },
}

if (system_bus) {
  const original_getService = system_bus.getService.bind(system_bus)
  system_bus.getService = function getService(...args) {
    const service = original_getService(...args)
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
    return service
  }
}
