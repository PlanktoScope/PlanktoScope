import { wakeup } from "./api/hardware.js"

export default function (RED) {
  function Node(config) {
    RED.nodes.createNode(this, config)
    const node = this
    node.on("input", function (msg, send, done) {
      wakeup(config.minutes)
        .then(() => {
          send(msg)
          done()
        })
        .catch(done)
    })
  }
  RED.nodes.registerType("wake up", Node)
}
