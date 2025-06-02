import { opendir, statfs } from "fs/promises"
import { join } from "path"
import mime from "mime"

async function* walk(dir) {
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
