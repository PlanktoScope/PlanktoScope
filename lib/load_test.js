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

function exit() {
  unload().finally(() => {
    process.exit()
  })
}

process.on("SIGINT", exit) // CTRL+C
process.on("SIGQUIT", exit) // Keyboard quit
process.on("SIGTERM", exit) // `kill` command
