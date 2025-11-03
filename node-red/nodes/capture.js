import { capture } from "../../lib/scope.js"

export default function (RED) {
  function Node(config) {
    RED.nodes.createNode(this, config)
    const node = this
    node.on("input", function (msg, send, done) {
      // msg.payload
      capture()
        .then(({ jpeg, dng }) => {
          msg.payload = { jpeg, dng }
          send(msg)
          done()
        })
        .catch(done)
    })
  }

  RED.nodes.registerType("capture", Node)
}
