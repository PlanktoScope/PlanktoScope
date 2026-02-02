import { focus, stopFocus, watch } from "../../lib/scope.js"

watch("status/focus").then(async (messages) => {
  for await (const message of messages) {
    console.log("focus", message)
  }
})

setTimeout(() => {
  stopFocus().catch(console.error)
}, 1000)

await focus({ direction: "UP", speed: 5, distance: 45 })
