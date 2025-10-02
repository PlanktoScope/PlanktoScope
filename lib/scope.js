import { pEvent } from "p-event"
import {
  client,
  publish,
  request,
  subscribe,
  unsubscribe,
  watch as mqttwatch,
} from "./mqtt.js"
import { rm } from "fs/promises"
import { restartService } from "./systemctl.js"
import { login, importFile, uploadFile } from "./ecotaxa.js"

function promiseMessage(topic, filter) {
  return pEvent(client, "message", {
    multiArgs: true,
    filter: ([t, data]) => {
      if (t !== topic) return false
      try {
        const payload = JSON.parse(data.toString())
        return filter(payload)
      } catch {
        return false
      }
    },
  })
}

export const BACKWARD = "BACKWARD"
export const FORWARD = "FORWARD"
export const UP = "UP"
export const DOWN = "DOWN"

export async function turnLightOn() {
  await subscribe("status/light")
  const promiseEvent = promiseMessage(
    "status/light",
    (payload) => payload?.status == "On",
  )
  await publish("light", { action: "on" })
  await promiseEvent
  await unsubscribe("status/light")
}

export async function turnLightOff() {
  await subscribe("status/light")
  const promiseEvent = promiseMessage(
    "status/light",
    (payload) => payload?.status == "Off",
  )
  await publish("light", { action: "off" })
  await promiseEvent
  await unsubscribe("status/light")
}

export async function focus(params) {
  await subscribe("status/focus")
  const promiseEvent = promiseMessage(
    "status/focus",
    (payload) => payload?.status == "Done",
  )
  await publish("actuator/focus", {
    action: "move",
    ...params,
  })
  await promiseEvent
  await unsubscribe("status/focus")
}

export async function stopFocus() {
  await subscribe("status/focus")
  const promiseEvent = promiseMessage(
    "status/focus",
    (payload) => payload?.status == "Interrupted",
  )
  await publish("actuator/focus", {
    action: "stop",
  })
  await promiseEvent
  await unsubscribe("status/focus")
}

export async function pump(params) {
  await subscribe("status/pump")
  const promiseEvent = promiseMessage(
    "status/pump",
    (payload) => payload?.status == "Done",
  )
  await publish("actuator/pump", {
    action: "move",
    ...params,
  })
  await promiseEvent
  await unsubscribe("status/pump")
}

export async function stopPump() {
  await subscribe("status/pump")
  const promiseEvent = promiseMessage(
    "status/pump",
    (payload) => payload?.status == "Interrupted",
  )
  await publish("actuator/pump", {
    action: "stop",
  })
  await promiseEvent
  await unsubscribe("status/pump")
}

export async function configure(config) {
  await subscribe("status/imager")
  const promiseEvent = promiseMessage(
    "status/imager",
    (payload) => payload?.status == "Config updated",
  )
  await publish("imager/image/update_config", {
    action: "update_config",
    config,
  })
  await promiseEvent
  await unsubscribe("status/imager")
}

export async function acquire(params) {
  await subscribe("status/imager")
  const promiseEvent = promiseMessage(
    "status/imager",
    (payload) => payload?.status == "Done",
  )
  await publish("imager/image", {
    action: "image",
    ...params,
  })
  await promiseEvent
  await unsubscribe("status/imager")
}

export async function segment(params) {
  await subscribe("status/segmenter")
  const promiseEvent = promiseMessage(
    "status/segmenter",
    (payload) => payload?.status == "Done",
  )
  await publish("segmenter/segment", {
    action: "segment",
    ...params,
  })
  await promiseEvent
  await unsubscribe("status/segmenter")
}

export async function restartSegmenter() {
  await restartService("planktoscope-org.segmenter")
}

export async function purgeData() {
  await rm("/home/pi/data/clean", { force: true, recursive: true })
}

export async function startBubbler() {
  await request("actuator/bubbler", { action: "on" })
}

export async function stopBubbler() {
  await request("actuator/bubbler", { action: "off" })
}

export async function upload({
  api_url,
  username,
  password,
  project_id,
  file_path,
}) {
  const token = await login({ api_url, username, password })

  const remote_path = await uploadFile({
    api_url,
    path: file_path,
    token,
  })

  const result = await importFile({
    api_url,
    path: remote_path,
    project_id,
    token,
  })

  return result
}

export async function watch(topic) {
  return mqttwatch(topic)
}
