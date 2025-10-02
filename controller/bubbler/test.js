import { startBubbler, stopBubbler, watch } from "../../lib/scope.js"
import { setTimeout } from "node:timers/promises"

watch("status/bubbler").then(async (messages) => {
  for await (const message of messages) {
    console.log("bubbler", message)
  }
})

console.log("start")
await startBubbler()

await setTimeout(2000)

console.log("stop")
await stopBubbler()
