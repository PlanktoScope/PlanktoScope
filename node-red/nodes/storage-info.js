import {
  countImageAcquired,
  countObjectSegmented,
  getStorageInfo,
} from "../../lib/stats.js"

export default function (RED) {
  function Node(config) {
    RED.nodes.createNode(this, config)
    const node = this
    node.on("input", function (msg, send, done) {
      Promise.all([
        countImageAcquired(),
        countObjectSegmented(),
        getStorageInfo(),
      ])
        .then(
          ([
            image_acquired,
            object_segmented,
            {
              percent_free: storage_percent_free,
              percent_used: storage_percent_used,
            },
          ]) => {
            msg.payload ??= {}
            Object.assign(msg.payload, {
              image_acquired,
              object_segmented,
              storage_percent_free,
              storage_percent_used,
            })
            send(msg)
            done()
          },
        )
        .catch(done)
    })
  }

  RED.nodes.registerType("storage info", Node)
}
