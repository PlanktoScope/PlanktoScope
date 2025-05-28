import { getHostname } from "./identity.js"

export default function (RED) {
  function Node(config) {
    RED.nodes.createNode(this, config)
    const node = this
    node.on("input", function (msg, send, done) {
      getHostname()
        .then((hostname) => {
          msg.payload ??= {}
          Object.assign(msg.payload, { hostname })
          send(msg)
          done()
        })
        .catch(done)
    })
  }

  RED.nodes.registerType("get-hostname", Node)
}
