#!/usr/bin/env node

import express from "express"
import path from "path"

import "./factory.js"
import "./setup.js"

process.title = "planktoscope-org.backend"

const app = express()

const path_spa = "/home/pi/PlanktoScope/frontend/dist"

app.use("/api/files", express.static("/home/pi/data"))
app.use("/", express.static(path_spa))
app.get("/{*splat}", (req, res) => {
  res.sendFile(path.resolve(path_spa, "index.html"))
})

app.listen(4000)
