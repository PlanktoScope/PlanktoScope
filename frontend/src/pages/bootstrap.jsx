import { createResource } from "solid-js"
import { useSubmission, action } from "@solidjs/router"

import { request } from "../../../lib/mqtt.js"

export default function Production() {
  const [EEPROM, { refetch }] = createResource(
    "bootstrap/init",
    async (topic) => {
      return request(topic)
    },
  )

  const updateBootstrapAction = action(async (data) => {
    data = Object.fromEntries(data.entries())

    data.custom_data = {
      serial_number: data.serial_number,
      hardware_version: data.hardware_version,
      eeprom_version: data.eeprom_version,
    }
    delete data.serial_number
    delete data.eeprom_version
    delete data.hardware_version

    await request("bootstrap/update", data)

    refetch()
  })

  const submission = useSubmission(updateBootstrapAction)

  let disabled = true

  return (
    <>
      <header>
        <h1>PlanktoScope</h1>
      </header>
      <main>
        <form action={updateBootstrapAction} method="post">
          <fieldset class="grid">
            <legend>
              <hgroup>
                <h4>Raspberry Pi HAT</h4>
                <p>Standard EEPROM fields</p>
              </hgroup>
            </legend>
            <div>
              <label>
                product_uuid
                <input
                  name="product_uuid"
                  readonly={disabled}
                  value={EEPROM()?.product_uuid}
                />
              </label>
              <label>
                product_id
                <input
                  name="product_id"
                  readonly={disabled}
                  value={EEPROM()?.product_id}
                />
              </label>
              <label>
                product_ver
                <input
                  name="product_ver"
                  readonly={disabled}
                  value={EEPROM()?.product_ver}
                />
              </label>
            </div>
            <div>
              <label>
                product
                <input
                  name="product"
                  readonly={disabled}
                  value={EEPROM()?.product}
                />
              </label>
              {/* <label>
                  current_supply
                  <input
                    name="current_supply"
                    type="number"
                    readonly={disabled}
                    value={EEPROM?.current_supply}
                  />
                </label>*/}
              <label>
                dt_blob
                <input
                  name="dt_blob"
                  readonly={disabled}
                  value={EEPROM()?.dt_blob}
                />
              </label>
              <label>
                vendor
                <input
                  name="vendor"
                  readonly={disabled}
                  value={EEPROM()?.vendor}
                />
              </label>
            </div>
          </fieldset>

          <hr />

          <fieldset class="grid">
            <legend>
              <hgroup>
                <h4>PlanktoScope</h4>
                <p>Custom EEPROM fields</p>
              </hgroup>
            </legend>
            <div>
              <label>
                serial_number
                <input
                  name="serial_number"
                  value={EEPROM()?.custom_data?.serial_number}
                />
              </label>
            </div>
            <div>
              <label>
                hardware_version
                <input
                  name="hardware_version"
                  value={EEPROM()?.custom_data?.hardware_version}
                />
              </label>
            </div>
            <label>
              eeprom_version
              <input
                name="eeprom_version"
                type="number"
                readonly={disabled}
                value={EEPROM()?.custom_data?.eeprom_version}
              />
            </label>
          </fieldset>

          <button
            disabled={EEPROM.loading || submission.pending}
            aria-busy={submission.pending}
            type="submit"
          >
            Save
          </button>
        </form>
      </main>
    </>
  )
}
