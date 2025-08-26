import { createResource, For } from "solid-js"
import { useSubmission, action, redirect } from "@solidjs/router"

import { request } from "/home/pi/PlanktoScope/lib/mqtt.js"

export default function Production() {
  const [data] = createResource("setup/read", async (topic) => {
    return request(topic)
  })

  const submitAction = action(async (data) => {
    data = Object.fromEntries(data.entries())
    await request("setup/update", data)
    throw redirect("/")
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
                      key={country.value}
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
                      key={timezone.value}
                      value={timezone.value}
                      selected={data()?.timezone === timezone.value}
                    >
                      {timezone.label}
                    </option>
                  )}
                </For>
              </select>
            </label>

            <Show when={data()?.hardware_versions}>
              <label>
                Model
                <select name="hardware_version">
                  <option disabled value="">
                    Pleasse select
                  </option>
                  <For each={data()?.hardware_versions}>
                    {(hardware_version) => (
                      <option
                        key={hardware_version.value}
                        value={hardware_version.value}
                        selected={
                          data()?.hardware_version === hardware_version.value
                        }
                      >
                        {hardware_version.label}
                      </option>
                    )}
                  </For>
                </select>
              </label>
            </Show>
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
