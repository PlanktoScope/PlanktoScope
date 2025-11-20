// import styles from "./styles.module.css"

import { createSignal, For } from "solid-js"

export default function Network() {
  const [wifis, setWifis] = createSignal([])

  getWifis().then(setWifis)

  return (
    <>
      <ul>
        <For each={wifis()} fallback={<div>Loading...</div>}>
          {(wifi) => <li>{wifi.ssid}</li>}
        </For>
      </ul>
    </>
  )
}

async function getWifis() {
  const url = new URL("/api/wifis", document.URL)
  url.port = 80
  try {
    const res = await fetch(url, {
      method: "GET",
    })
    const body = await res.json()
    return body
  } catch (err) {
    console.error(err)
  }
}
