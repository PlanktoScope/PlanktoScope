import { read, write } from "../../lib/eeprom.js"

await procedure("eeprom/led-operating-time", async (data) => {
  if (data.action == "get") {
    const eeprom = await read()
    return eeprom?.custom_data?.led_operating_time_seconds || 0
  }

  if (data.action == "increment") {
    const eeprom = await read()
    eeprom.custom_data ??= {}
    eeprom.custom_data.led_operating_time_seconds ??= 0
    eeprom.custom_data.led_operating_time_seconds += data.seconds
    await write(eeprom)
    return
  }

  if (data.action == "reset") {
    const eeprom = await read()
    eeprom.custom_data ??= {}
    eeprom.custom_data.led_operating_time_seconds = 0
    await write(eeprom)
    return
  }
})
