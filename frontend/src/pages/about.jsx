import { createEffect, Suspense } from "solid-js"
import AboutData from "./about.data"

export default function About() {
  const name = AboutData()

  createEffect(() => {
    console.log(name())
  })

  return (
    <section>
      <h1>About</h1>

      <p>A page all about this website.</p>

      <p>
        <span>We love</span>
        <Suspense fallback={<span>...</span>}>
          <span>&nbsp;{name()}</span>
        </Suspense>
      </p>
    </section>
  )
}
