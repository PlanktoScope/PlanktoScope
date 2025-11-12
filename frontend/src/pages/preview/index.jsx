/* globals MediaMTXWebRTCReader */

import Zoomist from "zoomist"
import "zoomist/css"

import styles from "./styles.module.css"
import "./reader.js"
import {
  startLight,
  capture,
  startBubbler,
  watch,
} from "../../../../lib/scope.js"
import { makeUrl } from "../../helpers.js"

import cameraIcon from "./camera.svg"

import NumberInput from "./NumberInput.jsx"
import { createSignal } from "solid-js"

export default function Preview() {
  let container
  let loader

  const [bubbler_dac, setBubblerDac] = createSignal(0)
  const [light_dac, setLightDac] = createSignal(0)

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

  watch("status/bubbler").then(async (messages) => {
    for await (const message of messages) {
      if (message.dac) {
        setBubblerDac(message.dac)
      }
    }
  })

  watch("status/light").then(async (messages) => {
    for await (const message of messages) {
      if (message.dac) {
        setLightDac(message.dac)
      }
    }
  })

  // ;(async () => {
  //   for (const message of await watch("light")) {
  //     console.log("wow", message)
  //   }
  //   for (const message of await watch("actuator/bubbler")) {
  //     console.log("wow", message)
  //   }
  // })()

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

  async function takeImage() {
    let result
    try {
      result = await capture()
    } catch (err) {
      console.error(err)
      return
    }

    console.log(result)
    window.open(makeUrl("/ps/data/browse/files/captures"), "_blank")
  }

  function onLightChange(dac) {
    startLight({
      dac,
    })
  }

  function onBubblerChange(dac) {
    startBubbler({
      dac,
    })
  }

  return (
    <>
      <div class={styles.controls}>
        <div>
          <h2>Light</h2>
          <NumberInput
            name="light"
            value={light_dac}
            onChange={onLightChange}
          />
        </div>
        <div>
          <h2>Bubbler</h2>
          <NumberInput
            name="bubler"
            value={bubbler_dac}
            onChange={onBubblerChange}
          />
        </div>
      </div>
      <div class={styles.preview}>
        <div ref={loader} class={styles.loader_container}>
          <span class={styles.loader} />
        </div>
        <div ref={container} hidden class="zoomist-container">
          <div class="zoomist-wrapper">
            <div class="zoomist-image">{video}</div>
          </div>
          <button
            tooltip="Take capture"
            class={styles.button_capture}
            onClick={takeImage}
          >
            {cameraIcon}
          </button>
        </div>
      </div>
    </>
  )
}
