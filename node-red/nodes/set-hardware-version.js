import { setHardwareVersion } from "/home/pi/PlanktoScope/lib/hardware.js"

export default function (RED) {
  function Node(config) {
    RED.nodes.createNode(this, config)
    const node = this
    node.on("input", function (msg, send, done) {
      const { hardware_version } = msg.payload
      setHardwareVersion(hardware_version)
        .then(() => {
          send(msg)
          done()
        })
        .catch(done)
    })
  }

  RED.nodes.registerType("set hardware version", Node)
}
