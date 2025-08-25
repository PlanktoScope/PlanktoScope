import { getTimezone } from "/home/pi/PlanktoScope/lib/timezone.js"

export default function (RED) {
  function Node(config) {
    RED.nodes.createNode(this, config)
    const node = this
    node.on("input", function (msg, send, done) {
      getTimezone()
        .then((timezone) => {
          msg.payload ??= {}
          msg.payload.timezone = timezone
          send(msg)
          done()
        })
        .catch(done)
    })
  }
  RED.nodes.registerType("get timezone", Node)
}
