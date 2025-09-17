// import { createResource, For, Show } from "solid-js"
// import { useSubmission, action, redirect } from "@solidjs/router"

export default function Production() {
  // const [data] = createResource("setup/read", async (topic) => {
  //   return request(topic)
  // })

  // const submitAction = action(async (data) => {
  //   data = Object.fromEntries(data.entries())
  //   await request("setup/update", data)
  //   throw redirect("/")
  // })

  // const submission = useSubmission(/*submitAction*/)
  return (
    <>
      <header>
        <h1>Developer Mode</h1>
      </header>
      <main>
        <form /*action={submitAction}*/ method="post">
          <fieldset>
            <legend>Configure Git</legend>

            <label>
              Please enter your name.
              <input name="name" type="text" placeholder="John Doe" />
            </label>

            <label>
              Please enter your email address.
              <input
                name="email"
                type="email"
                placeholder="john.doe@example.com"
              />
            </label>
          </fieldset>

          <button
            // disabled={data.loading || submission.pending}
            // aria-busy={submission.pending}
            type="submit"
          >
            Save
          </button>
        </form>
      </main>
    </>
  )
}
