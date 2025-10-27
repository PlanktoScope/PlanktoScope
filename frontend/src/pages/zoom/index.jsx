/* globals MediaMTXWebRTCReader */

import { onMount } from "solid-js"

import styles from "./styles.module.css"
import "../../../public/reader.js"
import { publish } from "../../../../lib/mqtt"

export default function Zoom() {
  const video = (
    <video class={styles.video} muted autoplay disablepictureinpicture />
  )

  const message = <div class={styles.message} />

  const setMessage = (str) => {
    message.innerText = str
  }

  publish("light", { action: "on" }).catch(console.error)

  const url = new URL(document.location)
  url.port = 8889
  url.pathname = "/cam/whep"
  const reader = new MediaMTXWebRTCReader({
    url,
    onError: (err) => {
      message.innerText = err
      setMessage(err)
    },
    onTrack: (evt) => {
      setMessage("")
      video.srcObject = evt.streams[0]
    },
  })

  window.addEventListener("beforeunload", () => {
    reader?.close()
  })

  return (
    <>
      <div>
        {video}
        {message}
      </div>
    </>
  )
}
