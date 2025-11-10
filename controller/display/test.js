import {
  startDisplay,
  stopDisplay,
  configureDisplay,
  watch,
} from "../../lib/scope.js"
import { setTimeout } from "node:timers/promises"

watch("display").then(async (messages) => {
  for await (const message of messages) {
    console.log("display", message)
  }
})

await startDisplay()

await configureDisplay({
  hostname: "foo",
  ip: "192.168.1.1",
})

// await setTimeout(2000)

// await stopDisplay()
