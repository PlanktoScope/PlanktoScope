import { writeSetup } from "../../lib/setup.js"

export default function (RED) {
  function Node(config) {
    RED.nodes.createNode(this, config)
    const node = this
    node.on("input", function (msg, send, done) {
      const { timezone, region } = msg.payload
      writeSetup({ timezone, region })
        .then(() => {
          msg.payload ??= {}
          // Object.assign(msg.payload, { setup })
          send(msg)
          done()
        })
        .catch(done)
    })
  }

  RED.nodes.registerType("write setup", Node)
}
