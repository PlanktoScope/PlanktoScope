import { startPump, stopPump, watch } from "../../lib/scope.js"
import { setTimeout } from "node:timers/promises"

watch("status/pump").then(async (messages) => {
    for await (const message of messages) {
        console.log("pump", message)
    }
})

await pump({ direction: "BACKWARD", flowrate: 10, volume: 0.5 })
