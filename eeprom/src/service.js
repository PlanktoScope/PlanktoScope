import mqtt from "mqtt"

process.title = "planktoscope-org.eeprom"

const client = mqtt.connect("mqtt://localhost:1883")

client.on("message", (topic, message) => {
  console.debug("message", topic, message.toString())
  client.end()
})

client.on("error", (err) => {
  console.error(err)
})

client.on("connect", () => {
  console.log("connected")
})

client.on("disconnect", () => {
  console.log("disconnected")
})

client.on("offline", () => {
  console.log("offline")
})

client.on("reconnect", () => {
  console.log("reconnect")
})
