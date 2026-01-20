import { segment, watch } from "../lib/scope.js"

watch("status/segmenter").then(async (messages) => {
  for await (const message of messages) {
    console.log("segmenter", message)
  }
})

console.time("segment")
await segment({
  path: ["/home/pi/data/img/BTS2023_S3_A2/"], // the acquisition path to segment
  settings: {
    force: true,
    recursive: false,
    ecotaxa_export: true, // generate an ecotaxa export archive
    keep: true, // save debug images - aka "/home/pi/data/clean"
    process_id: Date.now().toString().split("0.")[1], // the process id
    process_min_ESD: 20, // the minimum object size (we use area-equivalent diameter)
    remove_previous_mask: false, // see https://planktoscope.slack.com/archives/C01V5ENKG0M/p1714146253356569
  },
})
console.timeEnd("segment")
