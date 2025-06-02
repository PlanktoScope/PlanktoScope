import { readFile } from "fs/promises"
import child_process from "child_process"
import { promisify } from "util"

const execFile = promisify(child_process.execFile)

const path = "/run/machine-name"

export async function getName() {
  const data = await readFile(path, {
    encoding: "utf8",
  })

  return data.trim()
}

export async function getHostname() {
  const { stdout } = await execFile("hostnamectl", ["hostname"])

  return stdout.trim()
}
