import child_process from "child_process"
import { promisify } from "util"
import { getName, getHostname } from "./identity.js"
import { initConfigFiles, readSoftwareConfig } from "./file-config.js"
import {
  disableServices,
  enableServices,
  reload,
  restartService,
} from "./systemctl.js"
import { getSoftwareVersion } from "./software.js"
import { read as readEEPROM } from "./eeprom.js"

const execFile = promisify(child_process.execFile)

const hardware_versions = ["v3.0", "v2.6"].map((v) => {
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

  if (hardware_version == "v2.6") {
    await Promise.all([
      await disableServices(["planktoscope-org.controller.bubbler"]),
      await enableServices(["planktoscope-org.controller.light"]),
      await disableServices(["planktoscope-org.controller.display"]),
    ])
  } else if (hardware_version === "v3.0") {
    await enableServices([
      "planktoscope-org.controller.bubbler",
      "planktoscope-org.controller.light",
      "planktoscope-org.controller.display",
    ])
  }

  await Promise.all([
    restartService("nodered"),
    restartService("planktoscope-org.controller"),
  ])

  await reload()
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
      readEEPROM().catch(() => {}),
      getSoftwareVersion(),
    ])

  const serial_number = eeprom?.custom_data?.serial_number ?? null

  return {
    hardware_version,
    machine_name,
    hostname,
    serial_number,
    software_version,
  }
}
