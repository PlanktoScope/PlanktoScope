/* eslint n/no-top-level-await: off */
/* eslint no-empty: off */

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
} from "./scope.js"
import crypto from "crypto"
import { getHardwareVersion } from "./hardware.js"
import { Temporal, toTemporalInstant } from "@js-temporal/polyfill"
import { getName } from "./identity.js"
import path from "path"
import { rm } from "fs/promises"
Date.prototype.toTemporalInstant = toTemporalInstant

const hardware_version = await getHardwareVersion()
const machine_name = await getName()
let acquisition_path = null

function started(topic) {
  console.log("\n")
  console.log(new Date().toISOString(), "start", topic)
  console.time(topic)
  console.log("\n")
}

function completed(topic) {
  console.log("\n")
  console.log(new Date().toISOString(), "completed", topic)
  console.timeEnd(topic)
  console.log("\n")
}

const number_of_images = 3000
const flowcell_volume = 2.08 // μL

async function runSequence() {
  started("light on")
  await turnLightOn()
  completed("light on")

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
  await configure({
    sample_project: "Guirec_2025",
    sample_id,
    sample_operator: "FairScope Team",
    sample_sampling_gear: "single_location",
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
    acq_software: "PlanktoScopeOS-Guirec",
    object_date: date,
    object_time: time,
    object_lat: "0",
    object_lon: "0",
    object_depth_min: 0,
    object_depth_max: 0,
    process_pixel: 0.75,
    process_source: "github.com/PlanktoScope/PlanktoScope",
    process_commit: "82353c4b898f7485deaed52b2ae8b68c092713ca", // TODO
    acq_local_datetime: local_datetime,
    acq_camera_resolution: "4056x3040",
    acq_camera_iso: 150,
    acq_camera_shutter_speed: 125,
    acq_uuid: crypto.randomUUID(),
    sample_uuid: crypto.randomUUID(),
  })
  completed("configure")

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

  started("upload")
  const file_path = path.join(
    "/home/pi/data/export/ecotaxa/",
    `ecotaxa_${acquisition_id}.zip`,
  )
  await upload({
    username: "",
    password: "",
    project_id: "18353",
    file_path,
  })
  completed("upload")

  started("purge data")
  // await rm(file_path, { force: true })
  await purgeData()
  completed("purge data")
}

try {
  await runSequence()
} catch (err) {
  try {
    await turnLightOff()
  } catch {}
  throw err
}

process.exit()
