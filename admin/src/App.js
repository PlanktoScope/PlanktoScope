import "@picocss/pico/css/pico.blue.css"

import { useActionState, useCallback, useEffect, useState } from "react"
import { request, client, subscribe } from "./mqtt.js"

function usePromise(promise) {
  const [pending, setPending] = useState(true)
  const [result, setResult] = useState()
  const [error, setError] = useState()

  useEffect(() => {
    let ignore = false
    promise
      .then((result) => {
        console.log(result)
        if (!ignore) setResult(result)
      })
      .catch((error) => {
        if (!ignore) setError(error)
      })
      .finally(() => {
        if (!ignore) setPending(false)
      })
    return () => {
      ignore = true
    }
  }, [])

  return [pending, error, result]
}

export function App() {
  const [bootstrapPending, error, EEPROM] = usePromise(
    request("eeprom/bootsrap"),
  )
  const disabled = true

  const [_state, submitAction, updatePending] = useActionState(
    async (_previousState, formData) => {
      const data = Object.fromEntries(formData.entries())

      data.custom_data = {
        unit: data.unit,
      }
      delete data.unit

      await request("eeprom/update", data)
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
          <fieldset>
            <div className="grid">
              <div>
                <label>
                  product_uuid
                  <input
                    name="product_uuid"
                    disabled={disabled}
                    defaultValue={EEPROM?.product_uuid}
                  />
                </label>
                <label>
                  product_id
                  <input
                    name="product_id"
                    disabled={disabled}
                    defaultValue={EEPROM?.product_id}
                  />
                </label>
                <label>
                  product_ver
                  <input
                    name="product_ver"
                    disabled={disabled}
                    defaultValue={EEPROM?.product_ver}
                  />
                </label>
                <label>
                  vendor
                  <input
                    name="vendor"
                    disabled={disabled}
                    defaultValue={EEPROM?.vendor}
                  />
                </label>
              </div>
              <div>
                <label>
                  product
                  <input
                    name="product"
                    disabled={disabled}
                    defaultValue={EEPROM?.product}
                  />
                </label>
                <label>
                  current_supply
                  <input
                    name="current_supply"
                    type="number"
                    disabled={disabled}
                    defaultValue={EEPROM?.current_supply}
                  />
                </label>
                <label>
                  dt_blob
                  <input
                    name="dt_blob"
                    disabled={disabled}
                    defaultValue={EEPROM?.dt_blob}
                  />
                </label>
                <label>
                  unit
                  <input name="unit" defaultValue={EEPROM?.custom_data?.unit} />
                </label>
                <label>
                  eeprom_version
                  <input
                    name="eeprom_version"
                    defaultValue={EEPROM?.custom_data?.eeprom_version}
                  />
                </label>
              </div>
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
