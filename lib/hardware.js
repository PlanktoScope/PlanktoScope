import child_process from "child_process"
import { promisify } from "util"
import { getName, getHostname } from "./identity.js"
import { request } from "./mqtt.js"
import { initConfigFiles, readSoftwareConfig } from "./file-config.js"
import { setActiveNodeRedProject } from "./nodered.js"
import { restartService } from "./systemctl.js"
import { getSoftwareVersion } from "./software.js"

const execFile = promisify(child_process.execFile)

const hardware_versions = ["v3.0", "v2.6", "v2.5", "v2.3", "v2.1"].map((v) => {
  return { label: `PlanktoScope ${v}`, value: v }
})

export async function getHardwareVersions() {
  return hardware_versions
}

export async function getHardwareVersion() {
  const config = await readSoftwareConfig()
  return config?.acq_instrument?.split(" ")[1] || null
}

export async function setHardwareVersion(hardware_version) {
  await initConfigFiles(hardware_version)

  await setActiveNodeRedProject(
    hardware_version === "v2.1" ? "adafruithat" : "dashboard",
  )

  await Promise.all([
    restartService("nodered"),
    restartService("planktoscope-org.controller"),
  ])
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

export async function getMachineInfo() {
  const [hardware_version, machine_name, hostname, eeprom, software_version] =
    await Promise.all([
      getHardwareVersion(),
      getName(),
      getHostname(),
      // FIXME we should not use the bootstrap/read request here
      request("factory/read"),
      getSoftwareVersion(),
    ])

  return {
    hardware_version,
    machine_name,
    hostname,
    serial_number: eeprom?.custom_data?.serial_number ?? null,
    software_version,
  }
}
