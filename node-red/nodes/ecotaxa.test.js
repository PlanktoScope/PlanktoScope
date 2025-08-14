import { describe, afterEach, beforeEach, it } from "node:test"
import { createRequire } from "node:module"

import helper from "node-red-node-test-helper"
import ecotaxaNode from "./ecotaxa.js"

const require = createRequire(import.meta.url)
helper.init(require.resolve("node-red"))

describe("ecotaxa Node", function () {
  beforeEach(async () => {
    return new Promise((resolve) => {
      helper.startServer(resolve)
    })
  })

  afterEach(async () => {
    helper.unload()
    return new Promise((resolve) => {
      helper.stopServer(resolve)
    })
  })

  it("should be loaded", function (t, done) {
    const flow = [{ id: "n1", type: "ecotaxa", name: "ecotaxa" }]
    helper.load(ecotaxaNode, flow, function () {
      const n1 = helper.getNode("n1")
      t.assert.strictEqual(n1.name, "ecotaxa")
      done()
    })
  })
})
