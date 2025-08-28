import { readFile, writeFile } from "fs/promises"
import waitPort from "wait-port"
import { createRequire } from "node:module"

const require = createRequire(import.meta.url)

const node_red_project_config_path =
  "/home/pi/PlanktoScope/node-red/.config.projects.json"
const node_red_settings_path = "/home/pi/PlanktoScope/node-red/settings.cjs"

async function read() {
  const data = await readFile(node_red_project_config_path, "utf8")
  const config = await JSON.parse(data)
  return config
}

export async function getActiveNodeRedProject() {
  const config = await read()
  return config.activeProject
}

export async function setActiveNodeRedProject(project_name) {
  const config = await read()
  config.activeProject = project_name
  await writeFile(node_red_project_config_path, JSON.stringify(config, null, 4))
}

export async function promiseDashboardOnline() {
  const { uiPort: port } = require(node_red_settings_path)
  await waitPort({
    port,
  })
}
