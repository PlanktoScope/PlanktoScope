import mqtt from "mqtt"

const client = mqtt.connect("ws://pkscope-wax-ornament-42816:9001/", {
  protocolVersion: 5,
  properties: {
    requestResponseInformation: true,
  },
})

async function publish(topic, data, properties) {
  return client.publishAsync(
    topic,
    data !== undefined ? JSON.stringify(data) : undefined,
    properties,
  )
}

async function subscribe(topic) {
  return client.subscribeAsync(topic)
}

// async function unsubscribe(topic) {
//   return client.unsubscribeAsync(topic)
// }

const promises = new Map()
async function request(topic, data) {
  const id = Math.random().toString().split(".")[1]
  const responseTopic = `${topic}/${id}/response`

  await client.subscribeAsync(responseTopic)

  await publish(topic, data, {
    properties: {
      responseTopic,
    },
  })

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

client.on("message", (topic, message, packet) => {
  console.debug("mqtt message", { topic, message, packet })
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

export { client, request, publish, subscribe }
