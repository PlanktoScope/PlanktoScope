import { getMachineInfo } from "/home/pi/PlanktoScope/lib/hardware.js"

export default function (RED) {
  function Node(config) {
    RED.nodes.createNode(this, config)
    const node = this
    node.on("input", function (msg, send, done) {
      getMachineInfo()
        .then((machine_info) => {
          msg.payload ??= {}
          Object.assign(msg.payload, { machine_info })
          send(msg)
          done()
        })
        .catch(done)
    })
  }

  RED.nodes.registerType("get machine info", Node)
}
