import "../index.css"

import { createResource, For, Show } from "solid-js"
import { useSubmission, action } from "@solidjs/router"

import { request } from "../../../lib/mqtt.js"
import { makeUrl } from "../helpers.js"

export default function Setup() {
  const [data] = createResource("setup/read", async (topic) => {
    return request(topic)
  })

  const submitAction = action(async (data) => {
    data = Object.fromEntries(data.entries())
    await request("setup/update", data)
    window.location.replace(makeUrl("/"))
  })

  const submission = useSubmission(submitAction)
  return (
    <>
      <header>
        <h1>Welcome on the PlanktoScope GUI</h1>
      </header>
      <main>
        <form action={submitAction} method="post">
          <fieldset>
            <legend>Enter your information</legend>

            <label>
              Region
              <select name="country">
                <option disabled value="">
                  Pleasse select
                </option>
                <For each={data()?.countries}>
                  {(country) => (
                    <option
                      value={country.value}
                      selected={data()?.country === country.value}
                    >
                      {country.label}
                    </option>
                  )}
                </For>
              </select>
            </label>

            <label>
              Timezone
              <select name="timezone">
                <option disabled value="">
                  Pleasse select
                </option>
                <For each={data()?.timezones}>
                  {(timezone) => (
                    <option
                      value={timezone.value}
                      selected={data()?.timezone === timezone.value}
                    >
                      {timezone.label}
                    </option>
                  )}
                </For>
              </select>
            </label>
          </fieldset>

          <button
            disabled={data.loading || submission.pending}
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
