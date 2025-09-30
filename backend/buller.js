import { Chip, Line } from "node-libgpiod"
import { setTimeout } from "node:timers/promises"

const chip = new Chip(0)
const line = new Line(chip, 19)
line.requestOutputMode()

line.setValue(1)

await setTimeout(2000)

line.setValue(0)
