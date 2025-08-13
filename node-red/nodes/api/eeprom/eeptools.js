// Utils for https://github.com/raspberrypi/utils/tree/master/eeptools

import child_process from "node:child_process"
import { promisify } from "node:util"
import { tmpdir } from "node:os"
import { join } from "node:path"
import { readFile, mkdtemp, writeFile, rm } from "node:fs/promises"

const execFile = promisify(child_process.execFile)

/* eslint-disable no-useless-escape */
export function parse(content) {
  let data = {}

  let multiline = false
  let multiline_key = ""
  let multiline_value = null

  function addKey(key, value) {
    // number
    if (/^[0-9]+$/.test(value)) {
      data[key] = parseInt(value, 10)
      return
    }

    if (key !== "custom_data") {
      data[key] = value
      return
    }

    data["custom_data"] ??= []
    data["custom_data"].push(value)
  }

  function endMultiline() {
    addKey(multiline_key, multiline_value)
    multiline = false
    multiline_key = ""
    multiline_value = ""
  }

  function startMultiline(key) {
    multiline = true
    multiline_key = key
    multiline_value = ""
  }

  for (let line of content.split("\n")) {
    if (multiline) {
      if (line === "end") {
        endMultiline()
        continue
      }

      const idx = line.indexOf(`\"`)
      if (idx < 0) {
        multiline_value += line
      } else {
        multiline_value += line.slice(0, idx)
        endMultiline()
      }
      continue
    }

    if (line.startsWith("#") || !line) continue

    const idx = line.indexOf(" ")

    // multiline binary
    if (idx < 0) {
      startMultiline(line)
      continue
    }

    // multiline string
    const key = line.slice(0, idx)
    let value = line.slice(idx + 1)
    if (!value || value === '"') {
      startMultiline(key)
      continue
    }

    // vendor "FairScope"   # length=9
    value = value.split("#")[0].trim()
    if (value.startsWith(`"`) && value.endsWith(`"`)) {
      addKey(key, value.slice(1, -1))
    } else {
      addKey(key, value)
    }
  }

  return data
}

export function serialize(data) {
  let content = ""

  function castValue(key, value) {
    if (["product_uuid", "product_id", "product_ver"].includes(key))
      return value
    if (typeof value === "string") {
      return `"${value}"`
    } else return value
  }

  for (const [key, value] of Object.entries(data)) {
    if (Array.isArray(value)) {
      for (const v of value) {
        content += `${key} ${castValue(key, v)}\n`
      }
      continue
    }

    content += `${key} ${castValue(key, value)}\n`
  }

  return content
}

export async function write(data) {
  const tmp = await mkdtemp(join(tmpdir(), "eeptools-"))

  try {
    const file_txt = join(tmp, "content.txt")
    await writeFile(file_txt, serialize(data))

    const file_eep = join(tmp, "content.eep")
    await execFile("eepmake", [file_txt, file_eep])

    await execFile("sudo", [
      "eepflash.sh",
      "--yes",
      "--write",
      "--type=24c32",
      "--address=50",
      `--file=${file_eep}`,
    ])
  } finally {
    await rm(tmp, { force: true, recursive: true })
  }
}

export async function read() {
  const tmp = await mkdtemp(join(tmpdir(), "eeptools-"))

  try {
    const file_eep = join(tmp, "content.eep")
    await execFile("sudo", [
      "eepflash.sh",
      "--yes",
      "--read",
      "--type=24c32",
      "--address=50",
      `--file=${file_eep}`,
    ])

    const file_txt = join(tmp, "content.txt")
    await execFile("eepdump", [file_eep, file_txt])

    const txt = await readFile(file_txt, "utf8")
    return parse(txt)
  } finally {
    await rm(tmp, { force: true, recursive: true })
  }
}
