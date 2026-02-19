import { promisePortOpen } from "promise-port"

import { createRequire } from "node:module"

const require = createRequire(import.meta.url)

const node_red_settings_path = "/home/pi/PlanktoScope/node-red/settings.cjs"

export async function promiseDashboardOnline() {
  const { uiPort: port } = require(node_red_settings_path)
  await promisePortOpen(port)
}
