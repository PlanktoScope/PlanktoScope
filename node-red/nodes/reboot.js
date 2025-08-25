import { reboot } from "/home/pi/PlanktoScope/lib/hardware.js"

export default function (RED) {
  function Node(config) {
    RED.nodes.createNode(this, config)
    const node = this
    node.on("input", function (msg, send, done) {
      reboot()
        .then(() => {
          msg.payload ??= {}
          send(msg)
          done()
        })
        .catch(done)
    })
  }

  RED.nodes.registerType("reboot", Node)
}
