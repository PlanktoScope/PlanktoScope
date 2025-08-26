import { Suspense } from "solid-js"
import { A, useLocation } from "@solidjs/router"

function App(props) {
  // const location = useLocation()

  return (
    <>
      <nav>
        <ul>
          <li>
            <A href="/">Home</A>
          </li>
          <li>
            <A href="/bootstrap">Bootstrap</A>
          </li>
          <li>
            <A href="/setup">Setup</A>
          </li>
          <li>
            <A href="/about">About</A>
          </li>
          <li>
            <A href="/error">Error</A>
          </li>
        </ul>
      </nav>

      <main>
        <Suspense>{props.children}</Suspense>
      </main>
    </>
  )
}

export default App
