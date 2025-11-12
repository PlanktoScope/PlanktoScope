import styles from "./NumberInput.module.css"

export default function NumberInput(props) {
  let slider
  let number

  function onInput(evt) {
    slider.valueAsNumber = evt.target.valueAsNumber
    number.valueAsNumber = evt.target.valueAsNumber
    props.onChange?.(evt.target.valueAsNumber)
  }

  return (
    <div class={styles.div}>
      <input
        ref={slider}
        type="range"
        name={props.name}
        onInput={onInput}
        min="0"
        max="1"
        step="any"
      />
      <input
        ref={number}
        onInput={onInput}
        type="number"
        min="0"
        max="1"
        step="0.01"
      />
    </div>
  )
}
