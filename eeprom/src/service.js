import crypto from "node:crypto"

import mqtt from "mqtt"

import { read, write } from "./eeprom.js"

process.title = "planktoscope-org.eeprom"

const client = mqtt.connect("ws://pkscope-wax-ornament-42816:9001", {
  protocolVersion: 5,
  properties: {
    requestResponseInformation: true,
  },
})

const handlers = new Map()

async function handle(topic, handler) {
  await client.subscribeAsync(topic)
  handlers.set(topic, handler)
}

client.on("message", async (topic, message, packet) => {
  const handler = handlers.get(topic)
  if (!handler) return

  const responseTopic = packet.properties?.responseTopic
  if (!responseTopic) return

  async function respond(data) {
    await client.publishAsync(responseTopic, JSON.stringify(data))
  }

  let data
  if (message.length > 0) {
    try {
      data = JSON.parse(message.toString())
    } catch (err) {
      await respond({ error: err.message })
      return
    }
  }

  let result
  try {
    result = await handler(data)
  } catch (err) {
    console.error(err)
    await respond({ error: err.message })
    return
  }

  await respond({ result })
})

await handle("eeprom/bootsrap", async () => {
  const eeprom = await read()

  if (eeprom.custom_data?.eeprom_version !== 0) {
    return {
      product_uuid: crypto.randomUUID(),
      product_id: "0x0000", // TODO
      product_ver: "0x0000", //TODO
      vendor: "FairScope",
      product: "PlanktoScope HAT v3",
      current_supply: 0,
      dt_blob: "planktoscope-hat-v3",
      custom_data: {
        unit: "",
        eeprom_version: 0,
      },
    }
  }

  return eeprom
})

await handle("eeprom/update", async (data) => {
  await write(data)
})

client.on("message", (topic, message, packet) => {
  console.debug("mqtt message", { topic, message, packet })
})

client.on("error", (err) => {
  console.error("mqtt error", err)
})

client.on("connect", (packet) => {
  console.debug("mqtt connect", packet)
})

client.on("disconnect", () => {
  console.debug("mqtt disconnect")
})

client.on("offline", () => {
  console.debug("mqtt offline")
})

client.on("reconnect", () => {
  console.debug("mqtt reconnect")
})

// handle("/api/eeprom/bootstrap", async (req, res) => {
//     const eeprom = await read()
//     res.json(eeprom)
//     res.end()
// })

// app.get("/api/eeprom", async (req, res) => {
//     const eeprom = await read()
//     res.json(eeprom)
//     res.end()
// })

// app.post("/api/eeprom", async (req, res) => {
//     await write(req.body)
//     res.json(req.body)
//     res.end()
// })

// app.listen(port, () => {
//     console.log(`Example app listening on port ${port}`)
// })
