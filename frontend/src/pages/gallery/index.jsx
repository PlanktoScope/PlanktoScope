import styles from "./styles.module.css"

import { For, createSignal, Show } from "solid-js"
import { createInfiniteScroll } from "@solid-primitives/pagination"
import arrayShuffle from "array-shuffle"
import mediumZoom from "medium-zoom"
import { getObjects } from "../../../../lib/ecotaxa.js"

import Thumbnail from "./Thumbnail.jsx"

let total_pages
let window_size = 200
let window_start = 0

export default function Gallery() {
  const [pages, setEl, { end, setEnd }] = createInfiniteScroll(fetcher)

  const [zoomed, setZoomed] = createSignal(false)

  async function fetcher(page_number) {
    const { objects, total_ids } = await getObjects({
      // https://github.com/ecotaxa/ecotaxa_back/issues/64
      api_url: "http://pkscope-sponge-care-280/ecotaxa/api/",
      // No need for CORS for <img/>
      vault_url: "https://ecotaxa.obs-vlfr.fr/vault/",
      project_id: 15730,
      window_start,
      window_size,
    })
    window_start += objects.length
    total_pages = Math.ceil(total_ids / window_size)

    if (page_number === total_pages) setEnd(true)

    return arrayShuffle(objects)
  }

  const zoom = mediumZoom(null, {
    background: "rgba(243, 243, 243, 0.75)",
  })
  zoom.on("open", () => setZoomed(true))
  zoom.on("closed", () => setZoomed(false))

  return (
    <>
      <header data-theme="light">
        <h1>Gallery</h1>
      </header>

      <main data-theme="light">
        <div class={styles.gallery}>
          <For each={pages()}>
            {(object) => (
              <Thumbnail object={object} zoom={zoom} zoomed={zoomed()} />
            )}
          </For>
        </div>
        <Show when={!end()}>
          <h1 class={styles.loading} aria-busy="true" ref={setEl} />
        </Show>
      </main>
    </>
  )
}
