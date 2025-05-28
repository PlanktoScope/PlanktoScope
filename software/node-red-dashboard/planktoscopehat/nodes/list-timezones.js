import { getTimezones } from "./timezone.js"

export default function (RED) {
  function GetTimezonesNode(config) {
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
  RED.nodes.registerType("list timezones", GetTimezonesNode)
}
