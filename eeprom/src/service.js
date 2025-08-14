import mqtt from "mqtt"
import express from "express"
import { read, write } from "./eeprom.js"
import cors from "cors"

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

const app = express()
const port = process.env.PORT || 3001

app.use(cors())

app.get("/", (req, res) => {
  res.send("Hello World!")
})

app.get("/api/eeprom", async (req, res) => {
  const eeprom = await read()
  res.json(eeprom)
  res.end()
})

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})
