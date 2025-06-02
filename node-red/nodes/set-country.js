import { setWifiRegulatoryDomain } from "./api/country.js"

export default function (RED) {
  function Node(config) {
    RED.nodes.createNode(this, config)
    const node = this
    node.on("input", function (msg, send, done) {
      const { country } = msg.payload
      setWifiRegulatoryDomain(country)
        .then(() => {
          send(msg)
          done()
        })
        .catch(done)
    })
  }

  RED.nodes.registerType("set country", Node)
}
