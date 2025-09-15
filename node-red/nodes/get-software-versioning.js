import { getSoftwareVersioning } from "../../lib/software.js"

export default function (RED) {
  function Node(config) {
    RED.nodes.createNode(this, config)
    const node = this
    node.on("input", function (msg, send, done) {
      getSoftwareVersioning()
        .then((software_versioning) => {
          msg.payload ??= {}
          Object.assign(msg.payload, { software_versioning })
          send(msg)
          done()
        })
        .catch(done)
    })
  }

  RED.nodes.registerType("get software versioning", Node)
}
