import { startLight, stopLight, watch } from "../../lib/scope.js"
import { setTimeout } from "node:timers/promises"

watch("status/light").then(async (messages) => {
  for await (const message of messages) {
    console.log("light", message)
  }
})

await startLight()

await setTimeout(2000)

await stopLight()
