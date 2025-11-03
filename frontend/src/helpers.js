export function makeUrl(path) {
  const url = new URL(document.location.href)
  url.port = 80
  url.pathname = path
  return url
}

export function makeLocalUrl(path) {
  const url = new URL(document.location.href)
  url.pathname = path
  return url
}
