import { statfs } from "fs/promises"
import mime from "mime"

import { walk } from "./helpers.js"

export async function countImageAcquired() {
  let c = 0
  for await (const p of walk("/home/pi/data/img/")) {
    if (mime.getType(p)?.startsWith("image/")) {
      c++
    }
  }
  return c
}

export async function countObjectSegmented() {
  let c = 0
  for await (const p of walk("/home/pi/data/objects/")) {
    if (mime.getType(p)?.startsWith("image/")) {
      c++
    }
  }
  return c
}

export async function getStorageInfo() {
  const { blocks, bsize, bavail } = await statfs("/home/pi/", {
    bigint: false,
  })

  /* Total data blocks in filesystem */
  const total = blocks * bsize
  /* Free blocks in filesystem */
  // const free = bfree * bsize
  /* Free blocks available to unprivileged user */
  const avail = bavail * bsize

  const used = total - avail

  const percent_used = Math.round((100 * used) / total)
  const percent_free = Math.round((100 * avail) / total)

  return { percent_free, percent_used }
}
