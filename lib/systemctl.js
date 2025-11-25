import { pEvent } from "p-event"

import { system_bus } from "./dbus.js"

let service

try {
  service = system_bus.getService("org.freedesktop.systemd1")
} catch {}

let systemd_manager
async function get_systemd_manager() {
  if (!systemd_manager) {
    systemd_manager = await service.getInterface(
      "/org/freedesktop/systemd1",
      "org.freedesktop.systemd1.Manager",
    )
    await systemd_manager.Subscribe()
  }
  return systemd_manager
}

async function promiseJobComplete(systemd_manager, job_path) {
  return pEvent(systemd_manager, "JobRemoved", {
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
  const systemd_manager = await get_systemd_manager()
  const [job] = await systemd_manager.RestartUnit(
    normalizeUnitName(name),
    "replace",
  )
  return promiseJobComplete(systemd_manager, job)
}

export async function stopService(name) {
  const systemd_manager = await get_systemd_manager()
  const [job] = await systemd_manager.StopUnit(
    normalizeUnitName(name),
    "replace",
  )
  return promiseJobComplete(systemd_manager, job)
}

export async function startService(name) {
  const systemd_manager = await get_systemd_manager()
  const [job] = await systemd_manager.StartUnit(
    normalizeUnitName(name),
    "replace",
  )
  return promiseJobComplete(systemd_manager, job)
}

export async function enableServices(units = []) {
  const systemd_manager = await get_systemd_manager()
  await systemd_manager.EnableUnitFiles(
    units.map(normalizeUnitName),
    false, // runtime
    false, // force
  )
  await reload()
}

export async function disableServices(units = []) {
  const systemd_manager = await get_systemd_manager()
  await systemd_manager.DisableUnitFiles(
    units.map(normalizeUnitName),
    false, // runtime
  )
  await reload()
}

export async function reload() {
  const systemd_manager = await get_systemd_manager()
  await systemd_manager.Reload()
}
