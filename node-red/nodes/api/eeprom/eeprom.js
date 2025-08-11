import child_process from "node:child_process"
import { promisify } from "node:util"
import os from "node:os"
import path from "node:path"

import { Chip, Line } from "node-libgpiod"

const execFile = promisify(child_process.execFile)

async function writeEEPROM(custom) {
  const file_eep = path.join(os.tmpdir(), "planktoscope-hat.eep")

  await execFile("eepmake", [
    new URL(import.meta.resolve("./eeprom_settings.txt")).pathname,
    file_eep,
  ])

  const chip = new Chip(0)
  const eeprom_rp = new Line(chip, 26)
  eeprom_rp.requestOutputMode()
  eeprom_rp.setValue(0)

  await execFile("sudo", [
    "eepflash.sh",
    "--yes",
    "--write",
    "--type=24c32",
    "--address=50",
    `--file=${file_eep}`,
  ])

  eeprom_rp.release()
}

// ```sh
// eepmake eeprom_settings.txt planktoscope-hat.eep

// # write
// sudo gpioset -m signal gpiochip0 26=0 # disable write protect
// sudo eepflash.sh --yes --write --type=24c32 --address=50 --file=planktoscope-hat.eep
// ee

// # read
// sudo eepflash.sh --yes --read --type=24c32 --address=50 --file=dump.eep
// eepdump dump.eep dump.txt
// ```

// See https://github.com/raspberrypi/utils/blob/master/eeptools/eeprom_settings.txt

await writeEEPROM()
