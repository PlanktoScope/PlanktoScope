import { request } from "../../../lib/mqtt"

export default function Home() {
  request("setup/init")
    .then((data) => {
      window.location.href = data.redirect
    })
    .catch(console.error)

  return null
}
