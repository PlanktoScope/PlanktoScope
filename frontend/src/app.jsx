import { Suspense } from "solid-js"

function App(props) {
  return <Suspense>{props.children}</Suspense>
}

export default App
