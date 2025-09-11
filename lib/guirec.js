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
  restartSegmenter,
  purgeData,
} from "./scope.js"
import crypto from "crypto"
import { getHardwareVersion } from "./hardware.js"
import { Temporal, toTemporalInstant } from "@js-temporal/polyfill"
import { getName } from "./identity.js"
import path from "path"
Date.prototype.toTemporalInstant = toTemporalInstant

const hardware_version = await getHardwareVersion()
const machine_name = await getName()
let acquisition_path = null
console.log(hardware_version)

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

async function runSequence() {
  started("light on")
  await turnLightOn()
  completed("light on")

  started("flush")
  await pump({ direction: BACKWARD, volume: 10, flowrate: 10 })
  await pump({ direction: FORWARD, volume: 10, flowrate: 10 })
  completed("flush")

  started("configure")
  const t = Temporal.Now.plainDateTimeISO("UTC")
  const datetime = t.toString().split(".")[0]
  const date = Temporal.PlainDate.from(t).toString()
  const time = Temporal.PlainTime.from(t).toString().split(".")[0]
  const acq_id = datetime
  const sample_id = "Bag1" // TODO
  // FIXME: Segmenter should return the path instead
  acquisition_path = path.join("/home/pi/data/img/", date, sample_id, acq_id)
  await configure({
    sample_project: "Vigo_2025_chaetobloom", // TODO
    sample_id,
    sample_operator: "FairScope Team",
    sample_sampling_gear: "single_location",
    acq_id,
    acq_instrument: "PlanktoScope v2.6",
    acq_instrument_id: machine_name,
    acq_celltype: 300,
    acq_minimum_mesh: 20,
    acq_maximum_mesh: 300,
    acq_volume: "2", // TODO
    acq_magnification: "1.2",
    acq_fnumber_objective: 12,
    acq_nb_frame: 1, // TODO
    acq_software: "PlanktoScopeOS-Vigo_EMBL", // TODO
    object_date: date,
    object_time: time,
    object_lat: "42.2012", // TODO
    object_lon: "-8.8022", // TODO
    object_depth_min: 1,
    object_depth_max: 1,
    process_pixel: 0.75,
    process_source: "github.com/PlanktoScope/PlanktoScope",
    process_commit: "82353c4b898f7485deaed52b2ae8b68c092713ca", // TODO
    acq_local_datetime: datetime, // TODO
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
    volume: 0.01,
    nb_frame: 1, // TODO
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

  // started('upload')
  // await upload()
  // completed('upload')

  started("restart segmenter")
  await restartSegmenter()
  completed("restart segmenter")

  started("purge data")
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
