import dbus from "@homebridge/dbus-native"

const bus = dbus.createClient({
  busAddress: "unix:path=/run/dbus/system_bus_socket",
})
const service = bus.getService("org.freedesktop.systemd1")

let interf

function getInterface() {
  return new Promise((resolve, reject) => {
    service.getInterface(
      "/org/freedesktop/systemd1",
      "org.freedesktop.systemd1.Manager",
      (err, result) => {
        if (err) reject(err)
        else resolve(result)
      },
    )
  })
}

async function runMethod(method, ...args) {
  interf ??= await getInterface()

  return new Promise((resolve, reject) => {
    if (!interf)
      interf[method](...args, (err, result) => {
        if (err) reject(err)
        else resolve(result)
      })
  })
}

function normalizeUnitName(name) {
  if (name.endsWith(".service")) return name
  return name + ".service"
}

export async function restartService(name) {
  return runMethod("RestartUnit", normalizeUnitName(name), "replace")
}

export async function stopService(name) {
  return runMethod("StopUnit", normalizeUnitName(name), "replace")
}

export async function startService(name) {
  return runMethod("StartUnit", normalizeUnitName(name), "replace")
}
