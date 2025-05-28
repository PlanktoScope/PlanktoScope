const { describe, afterEach, beforeEach, it } = require("node:test")

const helper = require("node-red-node-test-helper")
const ecotaxaNode = require("./ecotaxa.js")
const { resolve } = require("path")

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

  it("should make payload lower case", function (t, done) {
    const flow = [
      { id: "n1", type: "ecotaxa", name: "ecotaxa", wires: [["n2"]] },
      { id: "n2", type: "helper" },
    ]
    helper.load(ecotaxaNode, flow, function () {
      const n2 = helper.getNode("n2")
      const n1 = helper.getNode("n1")
      n2.on("input", function (msg) {
        t.assert.strictEqual(msg.payload, "uppercase")
        done()
      })
      n1.receive({ payload: "UpperCase" })
    })
  })
})
