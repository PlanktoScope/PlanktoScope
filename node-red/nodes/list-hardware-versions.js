import { getHardwareVersions } from "/home/pi/PlanktoScope/lib/hardware.js"

export default function (RED) {
  function Node(config) {
    RED.nodes.createNode(this, config)
    const node = this
    node.on("input", function (msg, send, done) {
      getHardwareVersions()
        .then((hardware_versions) => {
          msg.payload ??= {}
          msg.payload.hardware_versions = hardware_versions
          send(msg)
        })
        .catch(done)
    })
  }

  RED.nodes.registerType("list hardware versions", Node)
}
