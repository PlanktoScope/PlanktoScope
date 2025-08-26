import { writeFile } from "fs/promises"

const node_red_project_config_path =
  "/home/pi/PlanktoScope/node-red/.config.projects.json"

async function read() {
  const { default: config } = await import(node_red_project_config_path, {
    with: { type: "json" },
  })
  return config
}

export async function getActiveNodeRedProject() {
  const config = await read()
  return config.activeProject
}

export async function setActiveNodeRedProject(project_name) {
  const config = await read()
  config.activeProject = project_name
  await writeFile(
    node_red_project_config_path,
    null,
    JSON.stringify(config, null, 4),
  )
}
