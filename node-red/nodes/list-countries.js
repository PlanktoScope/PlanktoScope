import { getWifiRegulatoryDomains } from "../../lib/country.js"

export default function (RED) {
  function Node(config) {
    RED.nodes.createNode(this, config)
    const node = this
    node.on("input", function (msg, send, done) {
      getWifiRegulatoryDomains()
        .then((domains) => {
          msg.payload ??= {}
          msg.payload.countries = domains
          send(msg)
        })
        .catch(done)
    })
  }

  RED.nodes.registerType("list countries", Node)
}
