// Utils for https://github.com/raspberrypi/utils/tree/master/eeptools

/* eslint-disable no-useless-escape */
export function parse(content) {
  let data = {}

  let multiline = false
  let multiline_key = ""
  let multiline_value = null

  function addKey(key, value) {
    // number
    if (/^[0-9]+$/.test(value)) {
      data[key] = parseInt(value, 10)
      return
    }

    if (key !== "custom_data") {
      data[key] = value
      return
    }

    data["custom_data"] ??= []
    data["custom_data"].push(value)
  }

  for (let line of content.split("\n")) {
    if (multiline) {
      multiline_value += line
      if (line.endsWith("end") || line.endsWith(`\"`)) {
        addKey(multiline_key, multiline_value)
        multiline = false
        multiline_key = ""
        multiline_value = ""
      }
      continue
    }

    if (line.startsWith("#") || !line) continue

    const idx = line.indexOf(" ")

    // multiline binary
    if (idx < 0) {
      multiline = true
      multiline_key = line
      multiline_value = ""
      continue
    }

    // multinline string
    const key = line.slice(0, idx)
    const value = line.slice(idx + 1)
    if (!value || value === '"') {
      multiline = true
      multiline_key = key
      multiline_value = ""
      continue
    }

    if (value.startsWith(`"`) && value.endsWith(`"`)) {
      addKey(key, value.slice(1, -1))
    } else {
      addKey(key, value)
    }
  }

  return data
}

export function serialize(data) {
  let content = ""

  function castValue(key, value) {
    if (["product_uuid", "product_id", "product_ver"].includes(key))
      return value
    if (typeof value === "string") {
      return `"${value}"`
    } else return value
  }

  for (const [key, value] of Object.entries(data)) {
    if (Array.isArray(value)) {
      for (const v of value) {
        content += `${key} ${castValue(key, v)}\n`
      }
      continue
    }

    content += `${key} ${castValue(key, value)}\n`
  }

  return content
}
