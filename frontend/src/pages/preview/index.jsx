/* globals MediaMTXWebRTCReader */

import styles from "./styles.module.css"
import "../../../public/reader.js"

export default function Preview() {
  const video = <video class={styles.video} muted autoplay />
  const message = <div class={styles.message} />

  const setMessage = (str) => {
    message.innerText = str
  }

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
      {video}
      {message}
    </>
  )
}
