import { after, before, suite, test } from "node:test"
import { parse } from "./eeptools.js"
import { write, read, isSupported } from "./eeprom.js"
import { readFileSync } from "node:fs"

suite("eeprom", { skip: !isSupported() }, () => {
  let original_eeprom_content
  before(async () => {
    original_eeprom_content = await read()
  })
  after(async () => {
    await write(original_eeprom_content)
  })

  test("write/read", async (t) => {
    const txt = readFileSync(
      new URL(import.meta.resolve("./fixtures/eeprom_settings.txt")),
      "utf8",
    )

    const parsed = parse(txt)
    parsed.product_uuid = "2f1f99eb-f799-47dd-aa1f-85274b5be49f"
    parsed.custom_data = { unit: "u320" }
    // current_supply was added recently and is not supported yet
    // by the version of raspi-utils-eeprom: /usr/bin/eepflash.sh in Raspberry Pi OS
    // https://github.com/raspberrypi/utils/commit/685afa8c0d6f2310eaefe1b528627a8bf3154ca0
    delete parsed.current_supply

    await write(parsed)

    t.assert.deepStrictEqual(await read(), parsed)
  })
})
