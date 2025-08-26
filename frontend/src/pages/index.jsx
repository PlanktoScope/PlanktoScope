import { request } from "../../../lib/mqtt"

export default function Home() {
  request("setup/init", { origin: window.location.origin })
    .then((data) => {
      window.location.href = data.redirect
    })
    .catch(console.error)

  return null
}
