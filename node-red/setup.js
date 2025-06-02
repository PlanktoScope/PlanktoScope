const fs = require("fs")
const path = require("path")

// This is a special case for legacy hardware; new hardware designs should all be part of the
// planktoscopehat codebase:
const CONFIG_PATH = "/home/pi/PlanktoScope/config.json"
function load_variant_setting(config_path = CONFIG_PATH) {
  let config = {}
  try {
    const file = fs.readFileSync(config_path, "utf8")
    try {
      config = JSON.parse(file)
    } catch (e) {
      console.error(`Couldn't parse ${config_path} as JSON file`)
      return undefined
    }
  } catch (e) {
    console.error(`Couldn't open ${config_path}`)
    return undefined
  }

  if (config.acq_instrument === undefined) {
    console.error(`${config_path} lacks a 'acq_instrument' field`)
    return undefined
  }

  if (config.acq_instrument === "PlanktoScope v2.1") {
    return "adafruithat"
  }
  return "planktoscopehat"
}

console.log("Determining configured hardware variant...")
let variant = load_variant_setting()
if (variant === undefined) {
  variant = "planktoscopehat"
  console.warn(
    `Couldn't load hardware variant setting from config, defaulting to ${variant}`
  )
}
console.log(`Hardware variant: ${variant}`)

const CONFIG_PROJECT_PATH = path.join(__dirname, ".config.projects.json")

const config = require(CONFIG_PROJECT_PATH)
config.activeProject = variant

fs.writeFileSync(CONFIG_PROJECT_PATH, JSON.stringify(config, null, 4))
