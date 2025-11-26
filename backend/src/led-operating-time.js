import { procedure, publish } from "../../lib/mqtt.js"
import { read, write } from "../../lib/eeprom.js"

await procedure("led-operating-time", async (data) => {
  if (data.action == "get") {
    const eeprom = await read()
    return eeprom?.custom_data?.led_operating_time || 0
  }

  if (data.action == "increment") {
    const eeprom = await read()
    eeprom.custom_data ??= {}
    eeprom.custom_data.led_operating_time ??= 0
    eeprom.custom_data.led_operating_time += parseInt(data.seconds, 10)
    await write(eeprom)
    await publishStatus(eeprom)
    return
  }

  if (data.action == "reset") {
    const eeprom = await read()
    eeprom.custom_data ??= {}
    eeprom.custom_data.led_operating_time = 0
    await write(eeprom)
    await publishStatus(eeprom)
    return
  }
})

async function publishStatus(eeprom) {
  try {
    await publish(
      "status/led-operating-time",
      { seconds: eeprom?.custom_data?.led_operating_time || 0 },
      null,
      {
        retain: true,
      },
    )
  } catch (err) {
    console.error(err)
  }
}

;(async () => {
  const eeprom = await read()
  await publishStatus(eeprom)
})()
