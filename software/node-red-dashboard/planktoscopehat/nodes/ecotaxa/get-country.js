import { getWifiRegulatoryDomain } from "./country.js"

export default function (RED) {
  function Node(config) {
    RED.nodes.createNode(this, config)
    const node = this
    node.on("input", function (msg, send, done) {
      getWifiRegulatoryDomain()
        .then((country) => {
          msg.payload ??= {}
          Object.assign(msg.payload, { country })
          send(msg)
          done()
        })
        .catch(done)
    })
  }

  RED.nodes.registerType("get-country", Node)
}
