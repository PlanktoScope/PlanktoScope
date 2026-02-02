import { configureDisplay, clearDisplay, watch } from "../../lib/scope.js"
import { setTimeout } from "timers/promises"

watch("display").then(async (messages) => {
  for await (const message of messages) {
    console.log("display", message)
  }
})

const url = `http://planktoscope-sponge-bob`

await configureDisplay({
  url,
})

await setTimeout(5000)
await clearDisplay()
