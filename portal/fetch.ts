export default function fetch(url, ...args) {
  return globalThis.fetch(
    new URL(url, "http://pkscope-sponge-care:8585", ...args)
  );
}
