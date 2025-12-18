import { test } from "node:test"
import { setTimeout } from "node:timers/promises"

import { cache } from "./helpers.js"

test("cached sync", async (t) => {
  const fn = t.mock.fn(() => "foo")

  const getFoo = cache(fn)

  t.assert.equal(fn.mock.callCount(), 0)
  t.assert.deepStrictEqual(getFoo(), "foo")
  t.assert.equal(fn.mock.callCount(), 1)
  t.assert.deepStrictEqual(getFoo(), "foo")
  t.assert.equal(fn.mock.callCount(), 1)

  t.assert.deepStrictEqual(await getFoo(), "foo")
})

test("cached async", async (t) => {
  const fn = t.mock.fn(async () => {
    await setTimeout(500)
    return "foo"
  })

  const getFoo = cache(fn)

  t.assert.equal(fn.mock.callCount(), 0)
  t.assert.deepStrictEqual(await getFoo(), "foo")
  t.assert.equal(fn.mock.callCount(), 1)
  t.assert.deepStrictEqual(await getFoo(), "foo")
  t.assert.equal(fn.mock.callCount(), 1)

  t.assert.equal(getFoo() instanceof Promise, true)
})

test("cached () => Promise", async (t) => {
  const fn = t.mock.fn(() => {
    return Promise.resolve("foo")
  })

  const getFoo = cache(fn)

  t.assert.equal(fn.mock.callCount(), 0)
  t.assert.deepStrictEqual(await getFoo(), "foo")
  t.assert.equal(fn.mock.callCount(), 1)
  t.assert.deepStrictEqual(await getFoo(), "foo")
  t.assert.equal(fn.mock.callCount(), 1)

  t.assert.equal(getFoo() instanceof Promise, true)
})
