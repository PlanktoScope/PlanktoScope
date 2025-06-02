import { getTimezone } from "./api/timezone.js"

export default function (RED) {
  function GetTimezoneNode(config) {
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
  RED.nodes.registerType("get timezone", GetTimezoneNode)
}
