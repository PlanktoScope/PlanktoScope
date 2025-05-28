import { setTimezone } from "./timezone.js"

export default function (RED) {
  function SetTimezoneNode(config) {
    RED.nodes.createNode(this, config)
    const node = this
    node.on("input", function (msg, send, done) {
      const { timezone } = msg.payload
      setTimezone({ timezone })
        .then(() => {
          send(msg)
          done()
        })
        .catch(done)
    })
  }
  RED.nodes.registerType("set timezone", SetTimezoneNode)
}
