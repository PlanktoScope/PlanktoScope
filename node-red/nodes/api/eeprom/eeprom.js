// https://github.com/raspberrypi/utils/tree/master/eeptools

import child_process from "node:child_process"
import { promisify } from "node:util"
import os from "node:os"
import path from "node:path"

import { Chip, Line } from "node-libgpiod"
import { readFile } from "node:fs/promises"

const execFile = promisify(child_process.execFile)

async function writeEEPROM() {
  const file_eep = path.join(os.tmpdir(), "planktoscope-hat.eep")

  await execFile("eepmake", [
    new URL(import.meta.resolve("./eeprom_settings.txt")).pathname,
    file_eep,
  ])

  const chip = new Chip(0)
  const eeprom_rp = new Line(chip, 26)
  eeprom_rp.requestOutputMode()
  eeprom_rp.setValue(0)

  try {
    await execFile("sudo", [
      "eepflash.sh",
      "--yes",
      "--write",
      "--type=24c32",
      "--address=50",
      `--file=${file_eep}`,
    ])
  } finally {
    eeprom_rp.setValue(1)
    eeprom_rp.release()
  }
}

async function readEEPROM() {
  const file_eep = path.join(os.tmpdir(), "planktoscope-hat_dump.eep")

  await execFile("sudo", [
    "eepflash.sh",
    "--yes",
    "--read",
    "--type=24c32",
    "--address=50",
    `--file=${file_eep}`,
  ])

  const file_dump = path.join(os.tmpdir(), "planktoscope-hat_dump.txt")
  await execFile("eepdump", [file_eep, file_dump])

  return await readFile(file_dump, "utf8")
}

async function updateEEPROM() {
  const content = await readEEPROM()
  const idx = content.lastIndexOf('custom_data "')

  const standard = content.slice(0, idx)

  const custom = content.slice(idx)

  console.log(custom)
}

await updateEEPROM()
