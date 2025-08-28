export default function About() {
  function makeUrl(path) {
    const url = new URL(document.location.href)
    url.port = 80
    url.pathname = path
    return url
  }

  function makeLocalUrl(path) {
    const url = new URL(document.location.href)
    url.pathname = path
    return url
  }

  return (
    <>
      <header>
        <h1>Bookmarks</h1>
      </header>

      <main>
        <ul>
          <li>
            <a href={makeLocalUrl("/bootstrap")} target="_blank">
              Bootstrap
            </a>
          </li>
          <li>
            <a href={makeLocalUrl("/setup")} target="_blank">
              Setup
            </a>
          </li>
          <li>
            <a href={makeLocalUrl("/gallery")} target="_blank">
              Gallery
            </a>
          </li>
          <li>
            <a href={makeUrl("/ps/node-red-v2/ui/")} target="_blank">
              Node-RED UI
            </a>
          </li>
          <li>
            <a href={makeUrl("/ps/node-red-v2/dashboard/")} target="_blank">
              Node-RED Dashboard
            </a>
          </li>
          <li>
            <a href={makeUrl("/ps/data/browse/")} target="_blank">
              File Manager
            </a>
          </li>
          <li>
            <a
              href={makeUrl("/admin/ps/device-backend-logs/browse/")}
              target="_blank"
            >
              Backend logs
            </a>
          </li>
          <li>
            <a href={makeUrl("/ps/docs/")} target="_blank">
              Docs
            </a>
          </li>
          <li>
            <a href={makeUrl("/admin/cockpit/")} target="_blank">
              Cockpit
            </a>
          </li>
          <li>
            <a href={makeUrl("/admin/fs/")} target="_blank">
              File Management
            </a>
          </li>
          <li>
            <a href={makeUrl("/admin/ps/node-red-v2/")} target="_blank">
              Node-RED flow editor
            </a>
          </li>
          <li>
            <a
              href={makeUrl("/ps/hal/camera/streams/preview.mjpg")}
              target="_blank"
            >
              Camera preview
            </a>
          </li>
          <li>
            <a
              href={makeUrl("/ps/processing/segmenter/streams/object.mjpg")}
              target="_blank"
            >
              Last segmented object
            </a>
          </li>
        </ul>
      </main>
    </>
  )
}
