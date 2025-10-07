import mqtt from "mqtt"
import { pEventIterator } from "p-event"

const hostname = globalThis?.location?.hostname || "localhost"

const client = mqtt.connect(`ws://${hostname}:9001/`, {
  protocolVersion: 5,
  properties: {
    requestResponseInformation: true,
  },
})

async function publish(topic, data, properties = {}, options = {}) {
  // let payloadFormatIndicator
  // let contentType

  if (data !== undefined) {
    data = JSON.stringify(data)
    // payloadFormatIndicator = 1
    // contentType = "application/json"
  }

  return client.publishAsync(topic, data, {
    properties: {
      // payloadFormatIndicator,
      // contentType,
      ...properties,
    },
    ...options,
  })
}

async function subscribe(topic) {
  return client.subscribeAsync(topic)
}

async function unsubscribe(topic) {
  return client.unsubscribeAsync(topic)
}

const promises = new Map()
async function request(topic, data) {
  const id = Math.random().toString().split(".")[1]
  const responseTopic = `${topic}/${id}/response`

  await client.subscribeAsync(responseTopic)

  await publish(
    topic,
    data,
    {
      responseTopic,
    },
    { qos: 1 },
  )

  const resolvers = Promise.withResolvers()
  promises.set(responseTopic, resolvers)
  return resolvers.promise
}

client.on("message", (topic, message /*packet*/) => {
  const resolvers = promises.get(topic)
  if (!resolvers) return

  let data
  try {
    data = JSON.parse(message)
    if (data.error) {
      resolvers.reject(data.error)
    } else {
      resolvers.resolve(data.result)
    }
  } catch (err) {
    resolvers.reject(err)
  } finally {
    promises.delete(topic)
  }
})

client.on("message", (topic, message, _packet) => {
  try {
    message = JSON.parse(message.toString())
  } catch {}
  client.emit(`message:${topic}`, message)
  console.debug("mqtt message", { topic, message })
})

client.on("connect", (packet) => {
  console.debug("mqtt connect", { packet })
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

client.on("error", (error) => {
  console.error("mqtt error", error)
})

const handlers = new Map()
export async function procedure(topic, handler) {
  await client.subscribeAsync(topic)
  handlers.set(topic, handler)
}

client.on("message", async (topic, message, packet) => {
  const handler = handlers.get(topic)
  if (!handler) return

  const { responseTopic, correlationData } = packet.properties || {}
  if (!responseTopic) return

  async function respond(data) {
    await publish(
      responseTopic,
      data,
      {
        correlationData,
        // payloadFormatIndicator: 1,
        // contentType: "application/json",
      },
      { qos: 1 },
    )
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

    // if (err instanceof z.ZodError) {
    //   await respond({
    //     error: { message: "Validation error", data: err.issues },
    //   })
    // } else {
    await respond({ error: { message: err.message } })
    // }
    // return
  }

  await respond({ result })
})

export async function watch(topic) {
  const iterator = pEventIterator(client, `message:${topic}`)
  await subscribe(topic)
  return iterator
}

export { client, request, publish, subscribe, unsubscribe }
