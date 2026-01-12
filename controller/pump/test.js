import { pump, stopPump, watch } from "../../lib/scope.js"

watch("status/pump").then(async (messages) => {
    for await (const message of messages) {
        console.log("pump", message)
    }
})

setTimeout(() => {
    stopPump().catch(console.error)
}, 1000)

await pump({ direction: "BACKWARD", flowrate: 10, volume: 1 })
