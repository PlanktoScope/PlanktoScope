export function createNodeFromAsync(type, fn, input, output) {
  return function (RED) {
    function Node(config) {
      RED.nodes.createNode(this, config)
      const node = this
      node.on("input", function (msg, send, done) {
        ;(async () => {
          const IN = await input(msg.payload)
          const result = await fn(IN)
          const OUT = await output(result)

          msg.payload ??= {}
          Object.assign(msg.payload, OUT)

          send(msg)

          done()
        })().catch(done)
      })
    }
    RED.nodes.registerType(type, Node)
  }
}
