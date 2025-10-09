import { startPump, stopPump, watch } from "../../lib/scope.js"
import { setTimeout } from "node:timers/promises"

watch("status/pump").then(async (messages) => {
  for await (const message of messages) {
    console.log("pump", message)
  }
})

await startPump({ direction: "BACKWARD", flowrate: 10, volume: 20 })

await setTimeout(2000)

await stopPump()
