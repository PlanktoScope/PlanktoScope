import dbus from "@homebridge/dbus-native"
import { pEvent } from "p-event"

let service
try {
  const bus = dbus.createClient({
    busAddress: "unix:path=/run/dbus/system_bus_socket",
  })
  service = bus.getService("org.freedesktop.systemd1")
} catch (err) {
  if (
    err instanceof TypeError &&
    err.message !== "net.createConnection is not a function"
  )
    throw err
}

let promise_interf
function getInterface() {
  promise_interf ??= new Promise((resolve, reject) => {
    service.getInterface(
      "/org/freedesktop/systemd1",
      "org.freedesktop.systemd1.Manager",
      (err, result) => {
        if (err) return reject(err)
        promise_interf = result
        runMethod("Subscribe")
          .then(() => {
            resolve(result)
          })
          .catch((err) => reject(err))
      },
    )
  })
  return promise_interf
}

async function runMethod(method, ...args) {
  const interf = await getInterface()
  return new Promise((resolve, reject) => {
    interf[method](...args, (err, ...result) => {
      if (err) reject(err)
      else resolve(result)
    })
  })
}

async function promiseJobComplete(job_path) {
  const interf = await getInterface()
  return pEvent(interf, "JobRemoved", {
    multiArgs: true,
    filter: ([id, job, unit, result]) => {
      if (job_path !== job) return false
      if (result !== "done") {
        throw new Error(
          `Job "${id}" for unit "${unit}" failed with result "${result}". `,
        )
      }
      return true
    },
  })
}

function normalizeUnitName(name) {
  if (name.endsWith(".service")) return name
  return name + ".service"
}

export async function restartService(name) {
  const [job] = await runMethod(
    "RestartUnit",
    normalizeUnitName(name),
    "replace",
  )
  return promiseJobComplete(job)
}

export async function stopService(name) {
  const [job] = await runMethod("StopUnit", normalizeUnitName(name), "replace")
  return promiseJobComplete(job)
}

export async function startService(name) {
  const [job] = await runMethod("StartUnit", normalizeUnitName(name), "replace")
  return promiseJobComplete(job)
}

export async function enableServices(units = []) {
  await runMethod(
    "EnableUnitFiles",
    units.map(normalizeUnitName),
    false, // runtime
    false, // force
  )
  await reload()
}

export async function disableServices(units = []) {
  await runMethod(
    "DisableUnitFiles",
    units.map(normalizeUnitName),
    false, // runtime
  )
  await reload()
}

export async function reload() {
  return runMethod("Reload")
}
