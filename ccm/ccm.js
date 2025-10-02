/* eslint n/no-top-level-await: off */
/* eslint no-empty: off */

// cp ccm.config.example.js ccm.config.js

import {
  turnLightOn,
  turnLightOff,
  pump,
  configure,
  acquire,
  BACKWARD,
  FORWARD,
  segment,
  purgeData,
  upload,
} from "../lib/scope.js"
import crypto from "node:crypto"
import { getHardwareVersion, poweroff } from "../lib/hardware.js"
import { Temporal, toTemporalInstant } from "@js-temporal/polyfill"
import { getName } from "../lib/identity.js"
import path from "node:path"
import { rm } from "node:fs/promises"
import { getSoftwareVersioning } from "../lib/software.js"
import { Client as GPSDClient } from "../lib/gpsd.js"
import { filesize } from "filesize"
import { stat } from "node:fs/promises"
import { setTimeout } from "node:timers/promises"

import config from "./ccm.config.js"
import { existsSync } from "node:fs"

import { WebClient } from "@slack/web-api"

import { client as mqtt } from "../lib/mqtt.js"

mqtt.on("message", (topic, message) => {
  try {
    message = JSON.parse(message.toString())
    if (!message?.status) return
  } catch {
    return
  }

  const { status, ...others } = message
  log(`mqtt ${topic}: ${status} ${JSON.stringify({ ...others })}`)
})

const config_safe = structuredClone(config)
config_safe.ecotaxa.password = "******"
config_safe.notifications.slack_token = "******"
console.log("config", config_safe)

Date.prototype.toTemporalInstant = toTemporalInstant

// Create a new instance of the WebClient class with the token read from your environment variable
const slack = new WebClient(config.notifications.slack_token)
function log(message) {
  const str = `${new Date().toISOString()} ${message}`

  console.log(str)
  slack.chat
    .postMessage({
      channel: config.notifications.slack_channel,
      text: config.project + " " + str,
    })
    .catch((err) => {
      console.error("Could not notify on slack", err)
    })
}

const hardware_version = await getHardwareVersion()
const machine_name = await getName()
let acquisition_path = null

const software = await getSoftwareVersioning()

let gpsd

if (config.location.gps === true) {
  gpsd = new GPSDClient()
  await gpsd.connect()
  await gpsd.watch({ json: true })

  // gpsd.on("response", (response) => {
  //   console.log(response)
  // })

  gpsd.on("error", (err) => {
    console.error(err)
  })
}

function started(topic) {
  log(`started ${topic}`)
}

function completed(topic) {
  log(`completed ${topic}`)
}

// 2x1000 images par jour
const number_of_images = config.number_of_images
const flowcell_volume = 2.08 // μL
const wait_seconds = 120

async function runSequence() {
  log(`online, waiting ${wait_seconds} seconds`)
  await setTimeout(wait_seconds * 1000)

  // Why make a backflush?
  started("cleaning tube backward")
  await pump({ direction: BACKWARD, volume: 10, flowrate: 10 })
  completed("cleaning tube backward")

  started("cleaning tube forward")
  await pump({ direction: FORWARD, volume: 10, flowrate: 10 })
  completed("cleaning tube forward")

  started("configure")
  const local_datetime = Temporal.Now.plainDateTimeISO().toString()
  const t = Temporal.Now.plainDateTimeISO("UTC")
  const datetime = t.toString().split(".")[0]
  const date = Temporal.PlainDate.from(t).toString()
  const time = Temporal.PlainTime.from(t).toString()
  const acquisition_id = `acquisition_${datetime}`
  const sample_id = `sample_${datetime}`
  // FIXME: Segmenter should return the path instead
  acquisition_path = path.join(
    "/home/pi/data/img/",
    date,
    sample_id,
    acquisition_id,
  )

  let object_lat
  let object_lon
  if (gpsd?.TPV) {
    object_lat = gpsd.TPV.lat
    object_lon = gpsd.TPV.lon
  } else if (config.location.latitude && config.location.longitude) {
    object_lat = config.location.latitude
    object_lon = config.location.longitude
  }

  const config_sample = {
    sample_project: config.project,
    sample_id,
    sample_operator: config.operator,
    sample_sampling_gear: config.sampling_gear,
    acq_id: acquisition_id,
    acq_instrument: `PlanktoScope ${hardware_version}`,
    acq_instrument_id: machine_name,
    acq_celltype: 300,
    acq_minimum_mesh: 20,
    acq_maximum_mesh: 300,
    acq_volume: (number_of_images * flowcell_volume) / 1000, // μL to mL
    acq_magnification: "1.2",
    acq_fnumber_objective: 12,
    acq_nb_frame: number_of_images,
    acq_software: `PlanktoScope OS ${software.version}`,
    object_date: date,
    object_time: time,
    object_lat,
    object_lon,
    object_depth_min: 0,
    object_depth_max: 0,
    process_pixel: 0.75,
    process_source: software.repo,
    process_commit: software.commit,
    acq_local_datetime: local_datetime,
    acq_camera_resolution: "4056x3040",
    acq_camera_iso: 150,
    acq_camera_shutter_speed: 125,
    // FIXME: for some reason ecotaxa uses acq_instrument_id as acq_uuid and sample_uuid
    acq_uuid: crypto.randomUUID(),
    sample_uuid: crypto.randomUUID(),
  }
  await configure(config_sample)
  completed("configure")

  started("light on")
  await turnLightOn()
  completed("light on")

  started("acquisition")
  await acquire({
    pump_direction: FORWARD,
    volume: 0.01, // Volume to pump between 2 images!
    nb_frame: number_of_images,
    sleep: 0.3,
  })
  completed("acquisition")

  started("light off")
  await turnLightOff()
  completed("light off")

  started("segmentation")
  await segment({
    path: [acquisition_path],
    settings: {
      force: false,
      recursive: true,
      ecotaxa: true,
      keep: true,
    },
  })
  completed("segmentation")

  const file_path_ecotaxa_zip = path.join(
    "/home/pi/data/export/ecotaxa/",
    `ecotaxa_${acquisition_id}.zip`,
  )

  if (
    existsSync(file_path_ecotaxa_zip) &&
    config.ecotaxa.upload === true &&
    config.ecotaxa.username &&
    config.ecotaxa.password &&
    config.ecotaxa.project_id
  ) {
    started("upload")

    const stats = await stat(file_path_ecotaxa_zip, { bigint: true })
    log(file_path_ecotaxa_zip + " " + filesize(stats.size))

    await upload({
      username: config.ecotaxa.username,
      password: config.ecotaxa.password,
      project_id: config.ecotaxa.project_id,
      file_path: file_path_ecotaxa_zip,
    })
    completed("upload")

    if (config.ecotaxa.remove_zip_after_upload === true) {
      await rm(file_path_ecotaxa_zip, { force: true })
    }
  }

  started("purge data")
  await purgeData()
  completed("purge data")
}

try {
  await runSequence()
} catch (err) {
  log("error " + err.toString())
  console.error(err)
} finally {
  try {
    await turnLightOff()
  } catch {}

  log(`done, waiting ${wait_seconds} seconds`)
  await setTimeout(wait_seconds * 1000)
}

log("poweroff 😴")
await poweroff()

// eslint-disable-next-line n/no-process-exit
process.exit()
