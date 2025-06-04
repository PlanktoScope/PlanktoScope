import { join } from "path"
import { opendir, readFile } from "fs/promises"

import mime from "mime"

const PATH_ACQUISITION = "/home/pi/data/img"

export async function listAcquisitions() {
  let acquisitions = []

  let fsdir
  try {
    fsdir = await opendir(PATH_ACQUISITION)
  } catch (err) {
    if (err.code !== "ENOENT") throw err
    return acquisitions
  }

  for await (const d of fsdir) {
    if (!d.isDirectory()) continue
    acquisitions.push(...(await listAcquisitionsForDate(d.name)))
  }

  return acquisitions
}

async function listAcquisitionsForDate(date) {
  let acquisitions = []

  let fsdir

  try {
    fsdir = await opendir(join(PATH_ACQUISITION, date))
  } catch (err) {
    if (err.code !== "ENOENT") throw err
    return acquisitions
  }

  for await (const d of fsdir) {
    if (!d.isDirectory()) continue
    acquisitions.push(
      ...(await listAcquisitionsFromDirectory(
        join(PATH_ACQUISITION, date, d.name)
      ))
    )
  }

  return acquisitions
}

async function listAcquisitionsFromDirectory(dir_path) {
  let acquisitions = []

  let fsdir

  try {
    fsdir = await opendir(dir_path)
  } catch (err) {
    if (err.code !== "ENOENT") throw err
    return acquisitions
  }

  for await (const d of fsdir) {
    if (!d.isDirectory()) continue

    const path = join(dir_path, d.name)
    const acquisition = await getAcquisitionFromPath(path)
    if (!acquisition) continue
    acquisitions.push(acquisition)
  }

  return acquisitions
}

async function getAcquisitionFromPath(path) {
  const metadata_path = join(path, "metadata.json")

  let metadata
  try {
    metadata = JSON.parse(await readFile(metadata_path))
  } catch {
    return
  }

  const project_name = metadata.sample_project
  const sample_id =
    metadata.sample_id.split(metadata.sample_project + "_")[1] ||
    metadata.sample_id
  const acquisition_id =
    metadata.acq_id.split(sample_id + "_")[1] || metadata.acq_id
  const operator_name = metadata.sample_operator
  const image_acquired_count = await countImageAcquired(path)
  // const is_segmented = null TODO

  const acquisition = {
    project_name,
    sample_id,
    acquisition_id,
    operator_name,
    image_acquired_count,
    is_segmented: null,
  }

  return acquisition
}

async function countImageAcquired(path) {
  let c = 0
  for await (const d of await opendir(path)) {
    if (!d.isFile()) continue
    if (mime.getType(d.name)?.startsWith("image/")) {
      c++
    }
  }
  return c
}
