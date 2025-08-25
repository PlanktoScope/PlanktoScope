import { getHardwareVersion } from "/home/pi/PlanktoScope/lib/hardware.js"

export default function (RED) {
  function Node(config) {
    RED.nodes.createNode(this, config)
    const node = this
    node.on("input", function (msg, send, done) {
      getHardwareVersion()
        .then((hardware_version) => {
          msg.payload ??= {}
          Object.assign(msg.payload, { hardware_version })
          send(msg)
          done()
        })
        .catch(done)
    })
  }

  RED.nodes.registerType("get hardware version", Node)
}
