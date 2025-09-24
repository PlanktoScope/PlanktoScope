import styles from "./styles.module.css"

import { For, createSignal, Show, onMount, createResource } from "solid-js"
import L, { Map, TileLayer, Marker, Circle, Polygon, Popup } from "leaflet"

import "leaflet/dist/leaflet.css"
import { getObjects } from "../../../../lib/ecotaxa"

// https://github.com/ecotaxa/ecotaxa_back/issues/64
const api_url = new URL("http://example.com/ecotaxa/api/")
api_url.hostname = document.location.hostname

// No need for CORS for <img/>
const vault_url = "https://ecotaxa.obs-vlfr.fr/vault/"

export default function MapPage() {
  let div_map

  onMount(() => {
    const map = new Map(div_map)
      // map.setZoom(2)
      .setView([48.587410962886686, -3.8383494867168175], 2)

    const tile_layer = new TileLayer(
      "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
      {
        maxZoom: 19,
        attribution:
          '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      },
    )
    tile_layer.addTo(map)

    getObjects({
      api_url,
      vault_url,
      project_id: 15730,
      window_start: 0,
      window_size: 5000,
    }).then((result) => {
      console.log(result)
      result.objects.forEach((object) => {
        if (object.latitude && object.longitude) {
          const market = new Marker([object.latitude, object.longitude])
          market.addTo(map)
        }
      })
    })

    // const marker = new Marker([48.587410962886686, -3.8383494867168175])
    // marker.addTo(map)
  })

  return (
    <>
      <header>
        <h1>Map</h1>
      </header>

      <main>
        <div ref={div_map} class={styles.map}></div>
      </main>
    </>
  )
}
