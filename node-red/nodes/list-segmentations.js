import { listSegmentations } from "./api/db.js"

export default function (RED) {
  function Node(config) {
    RED.nodes.createNode(this, config)
    const node = this
    node.on("input", function (msg, send, done) {
      listSegmentations()
        .then((segmentations) => {
          msg.payload = segmentations
          send(msg)
        })
        .catch(done)
    })
  }

  RED.nodes.registerType("list segmentations", Node)
}
