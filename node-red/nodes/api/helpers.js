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

import { opendir } from "fs/promises"
import { join } from "path"

export async function* walk(dir) {
  let fsdir
  try {
    fsdir = await opendir(dir)
  } catch (err) {
    if (err.code !== "ENOENT") throw err
    return
  }

  for await (const d of fsdir) {
    const entry = join(dir, d.name)
    if (d.isDirectory()) yield* walk(entry)
    else if (d.isFile()) yield entry
  }
}
