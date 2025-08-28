// Ecotaxa related APIs

import { handle } from "../../lib/mqtt.js"
import { getObjects } from "../../lib/ecotaxa.js"

await handle("ecotaxa/getObjects", async (data) => {
  return getObjects(data)
})
