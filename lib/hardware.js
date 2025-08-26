import { readFile } from "fs/promises"
import child_process from "child_process"
import { promisify } from "util"
import { getName, getHostname } from "./identity.js"
import { request } from "./mqtt.js"
import { parse } from "yaml"
import { initConfigFiles, readHardwareConfig } from "./file-config.js"
import { setActiveNodeRedProject } from "./nodered.js"

const execFile = promisify(child_process.execFile)

const hardware_versions = ["v3.0", "v2.6", "v2.5", "v2.3", "v2.1"].map((v) => {
  return { label: `PlanktoScope ${v}`, value: v }
})

export async function getHardwareVersions() {
  return hardware_versions
}

export async function getHardwareVersion() {
  const config = await readHardwareConfig()
  return config?.acq_instrument?.split(" ")[1] || null
}

export async function setHardwareVersion(hardware_version) {
  await initConfigFiles(hardware_version)

  await setActiveNodeRedProject(
    hardware_version === "v2.1" ? "adafruithat" : "dashboard",
  )

  // TODO: We must restart nodered and controller
  // await execFile("sudo", ["systemctl", "stop", "nodered"])
  // await execFile("sudo", ["systemctl", "stop", "planktoscope-org.controller"])

  // await execFile("sudo", ["systemctl", "start", "nodered"])
  // await execFile("sudo", ["systemctl", "start", "planktoscope-org.controller"])
}

async function resetWakeAlarm() {
  await execFile("sudo", ["sh", "-c", "echo 0 > /sys/class/rtc/rtc0/wakealarm"])
}

export async function reboot() {
  await resetWakeAlarm()
  await execFile("sudo", ["systemctl", "reboot"])
}

export async function poweroff() {
  await resetWakeAlarm()
  await execFile("sudo", ["systemctl", "poweroff"])
}

export async function wakeup(minutes) {
  await resetWakeAlarm()
  // https://www.linux.com/training-tutorials/wake-linux-rtc-alarm-clock/
  await execFile("sudo", [
    "sh",
    "-c",
    `echo \`date "+%s" -d "+ ${minutes} minutes"\` > /sys/class/rtc/rtc0/wakealarm`,
  ])
  await execFile("sudo", ["systemctl", "poweroff"])
}

async function getSoftwareVersion() {
  const path = "/usr/share/planktoscope/installer-versioning.yml"
  const data = await readFile(path, { encoding: "utf8" })
  const versioning = parse(data)
  return versioning.version
}

export async function getMachineInfo() {
  const [hardware_version, machine_name, hostname, eeprom, software_version] =
    await Promise.all([
      getHardwareVersion(),
      getName(),
      getHostname(),
      // FIXME we should not use the bootstrap/read request here
      request("bootstrap/read"),
      getSoftwareVersion(),
    ])

  return {
    hardware_version,
    machine_name,
    hostname,
    serial_number: eeprom?.custom_data?.serial_number,
    software_version,
  }
}
