/* eslint-disable no-useless-escape */
import { test } from "node:test"

import { parse, serialize } from "./eeptools.js"
import { readFileSync } from "node:fs"

test("parse eeprom_settings.txt", (t) => {
  const txt = readFileSync(
    new URL(import.meta.resolve("./fixtures/eeprom_settings.txt")),
    "utf8"
  )

  t.assert.deepStrictEqual(parse(txt), {
    product_uuid: "00000000-0000-0000-0000-000000000000",
    product_id: "0x0000",
    product_ver: "0x0000",
    vendor: "ACME Technology Company",
    product: "Special Sensor Board",
    current_supply: 0,
    dt_blob: "acme-sensor",
    custom_data: [
      "deadbeef c00 1c0d e",
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor\nincididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis\nnostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.\nDuis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore\neu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt\nin culpa qui officia deserunt mollit anim id est laborum.\n",
    ],
  })
})

test("parse eeprom_v1_settings.txt", (t) => {
  const txt = readFileSync(
    new URL(import.meta.resolve("./fixtures/eeprom_v1_settings.txt")),
    "utf8"
  )

  t.assert.deepStrictEqual(parse(txt), {
    product_uuid: "00000000-0000-0000-0000-000000000000",
    product_id: "0x0000",
    product_ver: "0x0000",
    vendor: "ACME Technology Company",
    product: "Special Sensor Board",
    back_power: 0,
    gpio_drive: 0,
    gpio_hysteresis: 0,
    gpio_slew: 0,
    custom_data: ["deadbeef c00 1c0d e"],
  })
})

test("parse example", (t) => {
  const txt = readFileSync(
    new URL(import.meta.resolve("./fixtures/example.txt")),
    "utf8"
  )

  t.assert.deepStrictEqual(parse(txt), {
    dt_blob: "rpi-dacpro",
    custom_data: [
      "This is the start of a long string.\n" +
        "End this line with a carriage return\\r\n" +
        "NUL-terminated\\0\n",
      "NL and NUL-terminated\n\\0\n",
      "End text with no NL",
      "End text with NL\n",
    ],
  })
})

test("parse with trailing comments", (t) => {
  t.assert.deepStrictEqual(parse(`foo bar # this is a comment`), {
    foo: "bar",
  })
})

test("parse with embedded double quote", (t) => {
  t.assert.deepStrictEqual(
    parse(
      `custom_data "
super"
cool"\\"`
    ),
    {
      custom_data: [`super"\ncool"`],
    }
  )
})

test("serialize", (t) => {
  const settings = {
    product_uuid: "00000000-0000-0000-0000-000000000000",
    product_id: "0x0000",
    product_ver: "0x0000",
    vendor: "ACME Technology Company",
    product: "Special Sensor Board",
    current_supply: 0,
    dt_blob: "acme-sensor",
    custom_data: [
      "deadbeef c00 1c0d e",
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor\nincididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis\nnostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.\nDuis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore\neu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt\nin culpa qui officia deserunt mollit anim id est laborum.\n",
    ],
  }

  const data = serialize(settings)

  t.assert.strictEqual(
    data,
    `product_uuid 00000000-0000-0000-0000-000000000000
product_id 0x0000
product_ver 0x0000
vendor "ACME Technology Company"
product "Special Sensor Board"
current_supply 0
dt_blob "acme-sensor"
custom_data "deadbeef c00 1c0d e"
custom_data "
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore
eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt
in culpa qui officia deserunt mollit anim id est laborum.
\\"
`
  )

  t.assert.deepStrictEqual(parse(data), settings)
})
