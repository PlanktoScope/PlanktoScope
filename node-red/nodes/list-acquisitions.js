import { listAcquisitions } from "./api/db.js"

export default function (RED) {
  function Node(config) {
    RED.nodes.createNode(this, config)
    const node = this
    node.on("input", function (msg, send, done) {
      listAcquisitions()
        .then((acquisitions) => {
          msg.payload = acquisitions
          // msg.payload.acquisitions = acquisitions
          send(msg)
        })
        .catch(done)
    })
  }

  RED.nodes.registerType("list acquisitions", Node)
}
