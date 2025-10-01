import {
  pump,
  stopPump,
  FORWARD,
  // focus,
  stopFocus,
  turnLightOn,
  turnLightOff,
  startBubbler,
  stopBubbler,
} from "./scope.js"
import { subscribe } from "./mqtt.js"

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

await subscribe("status/#")

async function load() {
  await Promise.all([
    turnLightOn(),
    startBubbler(),
    pump({ direction: FORWARD, flowrate: 50, volume: 20 * 1000 }),
  ])
}

async function unload() {
  await Promise.all([turnLightOff(), stopBubbler(), stopPump(), stopFocus()])
}

let exiting = false

function exit() {
  if (exiting) return
  exiting = true
  unload().finally(() => {
    process.exit()
  })
}

load()

process.on("SIGINT", exit) // CTRL+C
process.on("SIGQUIT", exit) // Keyboard quit
process.on("SIGTERM", exit) // `kill` command
