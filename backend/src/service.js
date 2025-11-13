#!/usr/bin/env node

import express from "express"
import path from "path"

import "./factory.js"
import "./setup.js"
import { readSoftwareConfig } from "../../lib/file-config.js"
import { getActiveNodeRedProject } from "../../lib/nodered.js"

process.title = "planktoscope-org.backend"

const app = express()

const path_spa = "/home/pi/PlanktoScope/frontend/dist"

app.use("/api/files", express.static("/home/pi/data"))
app.get("/", async (req, res) => {
  const software_config = await readSoftwareConfig()

  if (software_config?.user_setup !== true) {
    return res.redirect(302, "/setup")
  }

  const node_red_project = await getActiveNodeRedProject()
  return res.redirect(
    302,
    node_red_project === "dashboard"
      ? "/ps/node-red-v2/dashboard"
      : "/ps/node-red-v2/ui",
  )
})
app.use("/", express.static(path_spa))
app.get("/{*splat}", (req, res) => {
  res.sendFile(path.resolve(path_spa, "index.html"))
})

app.listen(4000)
