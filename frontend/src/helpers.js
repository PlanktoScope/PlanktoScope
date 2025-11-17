export function makeUrl(path) {
  const url = new URL(document.URL)
  url.port = 80
  url.pathname = path
  return url
}

export function makeLocalUrl(path) {
  const url = new URL(document.URL)
  url.pathname = path
  return url
}

export function triggerDownload(url) {
  const link = document.createElement("a")
  link.href = url.toString()
  link.download = ""
  link.target = "_blank"
  link.click()
}
