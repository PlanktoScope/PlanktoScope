import "@picocss/pico/css/pico.blue.css"
import { useActionState } from "react"
import useSWR from "swr"

import { request } from "./mqtt.js"

function fetcher(topic) {
  return request(topic)
}

function useTopic(topic, options) {
  const value = useSWR(topic, fetcher, options)
  return value
}

export function App() {
  const {
    isLoading: bootstrapPending,
    data: EEPROM,
    mutate: update,
  } = useTopic("eeprom/bootsrap", {
    revalidateIfStale: false,
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
  })

  const disabled = true

  const [, submitAction, updatePending] = useActionState(
    async (_previousState, formData) => {
      const data = Object.fromEntries(formData.entries())

      data.custom_data = {
        unit: data.unit,
        eeprom_version: data.eeprom_version,
      }
      delete data.unit
      delete data.eeprom_version

      await request("eeprom/update", data)

      update()

      return null
    },
    null,
  )

  return (
    <>
      <header>
        <h1>PlanktoScope</h1>
      </header>
      <main>
        <form action={submitAction}>
          <fieldset className="grid">
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
                  readOnly={disabled}
                  defaultValue={EEPROM?.product_uuid}
                />
              </label>
              <label>
                product_id
                <input
                  name="product_id"
                  readOnly={disabled}
                  defaultValue={EEPROM?.product_id}
                />
              </label>
              <label>
                product_ver
                <input
                  name="product_ver"
                  readOnly={disabled}
                  defaultValue={EEPROM?.product_ver}
                />
              </label>
            </div>
            <div>
              <label>
                product
                <input
                  name="product"
                  readOnly={disabled}
                  defaultValue={EEPROM?.product}
                />
              </label>
              {/* <label>
                  current_supply
                  <input
                    name="current_supply"
                    type="number"
                    readOnly={disabled}
                    defaultValue={EEPROM?.current_supply}
                  />
                </label>*/}
              <label>
                dt_blob
                <input
                  name="dt_blob"
                  readOnly={disabled}
                  defaultValue={EEPROM?.dt_blob}
                />
              </label>
              <label>
                vendor
                <input
                  name="vendor"
                  readOnly={disabled}
                  defaultValue={EEPROM?.vendor}
                />
              </label>
            </div>
          </fieldset>

          <hr></hr>

          <fieldset className="grid">
            <legend>
              <hgroup>
                <h4>PlanktoScope</h4>
                <p>Custom EEPROM fields</p>
              </hgroup>
            </legend>
            <div>
              <label>
                unit
                <input name="unit" defaultValue={EEPROM?.custom_data?.unit} />
              </label>
            </div>
            <div>
              <label>
                eeprom_version
                <input
                  name="eeprom_version"
                  type="number"
                  readOnly
                  defaultValue={EEPROM?.custom_data?.eeprom_version}
                />
              </label>
            </div>
          </fieldset>

          <button
            disabled={bootstrapPending || updatePending}
            aria-busy={updatePending}
            type="submit"
          >
            Save
          </button>
        </form>
      </main>
      <footer>
        Made with ❤️ by <a href="https://fairscope.com/">FairScope</a> in
        Bretagne
      </footer>
    </>
  )
}
