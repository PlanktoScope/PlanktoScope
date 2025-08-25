import { getTimezones } from "/home/pi/PlanktoScope/lib/timezone.js"

export default function (RED) {
  function Node(config) {
    RED.nodes.createNode(this, config)
    const node = this
    node.on("input", function (msg, send, done) {
      getTimezones()
        .then((timezones) => {
          msg.payload ??= {}
          msg.payload.timezones = timezones
          send(msg)
        })
        .catch(done)
    })
  }
  RED.nodes.registerType("list timezones", Node)
}
