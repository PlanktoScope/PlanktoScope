import { readSetup } from "../../lib/setup.js"

export default function (RED) {
  function Node(config) {
    RED.nodes.createNode(this, config)
    const node = this
    node.on("input", function (msg, send, done) {
      readSetup()
        .then((setup) => {
          msg.payload ??= {}
          Object.assign(msg.payload, { ...setup })
          send(msg)
          done()
        })
        .catch(done)
    })
  }

  RED.nodes.registerType("read setup", Node)
}
