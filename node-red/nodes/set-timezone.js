import { setTimezone } from "/home/pi/PlanktoScope/lib/timezone.js"

export default function (RED) {
  function Node(config) {
    RED.nodes.createNode(this, config)
    const node = this
    node.on("input", function (msg, send, done) {
      const { timezone } = msg.payload
      setTimezone(timezone)
        .then(() => {
          send(msg)
          done()
        })
        .catch(done)
    })
  }
  RED.nodes.registerType("set timezone", Node)
}
