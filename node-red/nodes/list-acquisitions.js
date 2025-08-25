import { listAcquisitions } from "/home/pi/PlanktoScope/lib/db.js"

export default function (RED) {
  function Node(config) {
    RED.nodes.createNode(this, config)
    const node = this
    node.on("input", function (msg, send, done) {
      listAcquisitions()
        .then((acquisitions) => {
          msg.payload = acquisitions
          send(msg)
        })
        .catch(done)
    })
  }

  RED.nodes.registerType("list acquisitions", Node)
}
