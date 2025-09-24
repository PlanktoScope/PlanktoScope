export default function Bookmarks() {
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
        <h2>Users</h2>

        <ul>
          <li>
            <a href={makeLocalUrl("/")} target="_blank">
              Dashboard
            </a>
          </li>
          <li>
            <a href={makeUrl("/ps/data/browse/files/")} target="_blank">
              Gallery
              {/* FIXME */}
            </a>
          </li>
          <li>
            <a href={makeUrl("/ps/data/browse/")} target="_blank">
              File Browser
              {/* FIXME */}
            </a>
          </li>
          <li>
            <a href={makeUrl("/ps/docs/")} target="_blank">
              Docs
            </a>
          </li>
        </ul>

        <h2>Developers</h2>

        <ul>
          <li>
            <a
              href={makeUrl("/admin/cockpit/system/logs#/?priority=info")}
              target="_blank"
            >
              Logs
            </a>
          </li>
          <li>
            <a href={makeUrl("/admin/cockpit/system/terminal")} target="_blank">
              Terminal
            </a>
          </li>

          <li>
            <a href={makeUrl("/admin/cockpit/")} target="_blank">
              Cockpit
            </a>
          </li>
          <li>
            <a href={makeUrl("/admin/fs/")} target="_blank">
              File Browser
            </a>
          </li>
          <li>
            <a href={makeUrl("/admin/ps/node-red-v2/")} target="_blank">
              Node-RED flow editor
            </a>
          </li>
          <li>
            <a
              href={makeUrl("/ps/processing/segmenter/streams/object.mjpg")}
              target="_blank"
            >
              {/* FIXME does it work? */}
              Last segmented object
            </a>
          </li>
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
            <a href={makeUrl("/ps/node-red-v2/ui/")} target="_blank">
              Node-RED UI
            </a>
          </li>
          <li>
            <a href={makeUrl("/ps/node-red-v2/dashboard/")} target="_blank">
              Node-RED Dashboard
            </a>
          </li>
        </ul>

        <h2>Experiments</h2>

        <ul>
          <li>
            <a href={makeLocalUrl("/preview")} target="_blank">
              Camera preview
            </a>
          </li>
          <li>
            <a href={makeLocalUrl("/gallery")} target="_blank">
              Ecotaxa Project Gallery
            </a>
          </li>
          <li>
            <a href={makeLocalUrl("/developer-mode")} target="_blank">
              Developer Mode
            </a>
          </li>
        </ul>
      </main>
    </>
  )
}
