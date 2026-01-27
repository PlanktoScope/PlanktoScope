import { configureDisplay, clearDisplay, watch } from "../../lib/scope.js"
import { setTimeout } from "timers/promises"

watch("display").then(async (messages) => {
  for await (const message of messages) {
    console.log("display", message)
  }
})

const online = false
const url = `http://192.168.4.1`

await configureDisplay({
  url,
  online,
})

await setTimeout(5000)

await clearDisplay()
