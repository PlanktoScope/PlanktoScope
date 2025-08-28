import { onCleanup, onMount } from "solid-js"
import styles from "./styles.module.css"

export default function Thumbnail(props) {
  const img = (
    <img
      data-zoom-src={props.object.file.url}
      loading="lazy"
      class={styles.img}
      src={props.object.thumbnail.url}
      alt={props.object.label}
    />
  )

  onMount(() => {
    props.zoom.attach(img)
  })

  onCleanup(() => {
    props.zoom.detach(img)
  })

  return (
    <a
      class={styles.thumbnail}
      href={props.object.file.url}
      // Hide tooltip on zoom
      // medium-zoom creates a background that desactives interaction with the document
      // so the tooltip stays on when zooming an image
      data-tooltip={props.zoomed ? null : props.object.label}
      onClick={(evt) => {
        evt.preventDefault()
      }}
    >
      {img}
    </a>
  )
}
