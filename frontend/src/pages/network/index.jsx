import { request, watch } from "../../../../lib/mqtt"
import "../../index.css"

// import styles from "./styles.module.css"

import { createResource, createSignal, For } from "solid-js"

export default function Network() {
  const [wifis] = createWatch("config/wifis")
  const [scanning, { refetch: scan }] = createResource(() =>
    request("config/wifis/scan"),
  )

  return (
    <div>
      <button aria-busy={scanning.loading} onClick={scan}>
        Rescan
      </button>
      <ul>
        <For each={wifis()} fallback={<div>Loading...</div>}>
          {(wifi) => (
            <li>
              <button onClick={() => request("config/wifis/connect", wifi)}>
                {wifi.ssid}
              </button>
            </li>
          )}
        </For>
      </ul>
    </div>
  )
}

function createWatch(topic) {
  const [data, setData] = createSignal([])

  watch(topic).then(async (iter) => {
    for await (const data of iter) {
      setData(data)
    }
  })

  return [data]
}
