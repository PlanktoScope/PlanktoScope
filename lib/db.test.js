import { test } from "node:test"
import { getGalleryPath } from "./db.js"

test("getGalleryPath", (t) => {
  t.assert.equal(
    getGalleryPath("/home/pi/data/objects/foo"),
    "/ps/data/browse/files/objects/foo",
  )
  t.assert.equal(
    getGalleryPath("/home/pi/data/img/foo"),
    "/ps/data/browse/files/img/foo",
  )
  t.assert.equal(getGalleryPath("/tmp/baz"), null)
})
