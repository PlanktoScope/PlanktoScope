/* globals MediaMTXWebRTCReader */

import Zoomist from "zoomist"
import "zoomist/css"

import styles from "./styles.module.css"
import "../../../public/reader.js"
import { startLight, capture } from "../../../../lib/scope.js"

import cameraIcon from "./camera.svg"

export default function Preview() {
  let container
  let loader

  const video = (
    <video
      on:loadedmetadata={onVideoLoad}
      class={styles.video}
      muted
      autoplay
      disablepictureinpicture
      preload="auto"
    />
  )

  startLight().catch(console.error)

  function onVideoLoad() {
    container.hidden = false
    // For some reason loader.hidden = true does not work
    loader.style.display = "none"
    new Zoomist(container, {
      slider: true,
      zoomer: true,
      maxScale: 4,
      zoomRatio: 0.1,
    })
  }

  const url = new URL(document.location)
  url.port = 8889
  url.pathname = "/cam/whep"
  const reader = new MediaMTXWebRTCReader({
    url,
    onError: (err) => {
      console.error("mediamtx error", err)
    },
    onTrack: (evt) => {
      console.debug("mediamtx track", evt)
      video.srcObject = evt.streams[0]
    },
  })

  window.addEventListener("beforeunload", () => {
    reader?.close()
  })

  return (
    <>
      <div ref={loader} class={styles.loader_container}>
        <span class={styles.loader}></span>
      </div>
      <div ref={container} hidden class="zoomist-container">
        <div class="zoomist-wrapper">
          <div class="zoomist-image">{video}</div>
        </div>
        <button
          class={styles.button_capture}
          onClick={() => capture().catch(console.error)}
        >
          {cameraIcon}
        </button>
      </div>
    </>
  )
}
