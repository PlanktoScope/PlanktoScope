// https://ecotaxa.obs-vlfr.fr/api/docs
// https://ecotaxa.obs-vlfr.fr/gui/prj/create

export const URL_API = "https://ecotaxa.obs-vlfr.fr/api/"

async function fetch(url, ...args) {
  const response = await globalThis.fetch(url, ...args)
  if (!response.ok) {
    let err = new Error(`Ecotaxa responded to ${url} with ${response.status}`)
    try {
      err.body = await response.json()
    } catch {}
    throw err
  }
  return response
}

export async function login({ api_url = URL_API, username, password }) {
  const req = await fetch(new URL("login", api_url), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  })
  const token = await req.json()
  return token
}

export async function getObjects({
  api_url = URL_API,
  vault_url = new URL("/vault/", api_url),
  project_id,
  window_start = 0,
  window_size = 100,
}) {
  const url = new URL(`object_set/${project_id}/query`, api_url)

  const fields = [
    "img.file_name",
    "img.width",
    "img.height",
    "img.thumb_file_name",
    "img.thumb_width",
    "img.thumb_height",
    "txo.display_name",
  ]

  url.search = new URLSearchParams({
    fields,
    // pagination
    window_start,
    window_size,
  })

  const response = await fetch(url, {
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({}),
    method: "POST",
  })

  const result = await response.json()

  const { object_ids, total_ids, details } = result

  const objects = object_ids.map((object_id, idx) => {
    const file_name = details[idx][0]
    const width = details[idx][1]
    const height = details[idx][2]
    const thumb_file_name = details[idx][3]
    const thumb_width = details[idx][4]
    const thumb_height = details[idx][5]
    const label = details[idx][6]

    const url = new URL(file_name, vault_url)
    const thumb_url = new URL(thumb_file_name || file_name, vault_url)

    return {
      label,
      file: {
        url: url,
        width,
        height,
      },
      thumbnail: {
        url: thumb_url,
        width: thumb_width,
        height: thumb_height,
      },
    }
  })

  return { objects, total_ids }
}

// async function createProject({api_url, token, title }) {
//   const req = await fetch(new URL("projects/create", api_url), {
//     method: "POST",
//     headers: {
//       "Content-Type": "application/json",
//       Authorization: `Bearer ${token}`,
//     },
//     body: JSON.stringify({
//       // "clone_of_id": 2,
//       title: "My new project title",
//       // "instrument": "PlanktoScope test",
//       // "visible": True,
//     }),
//   })
//   const project_id = await req.json()
//   return project_id
// }

export async function uploadFile({ api_url = URL_API, token, path }) {
  const { openAsBlob } = await import("node:fs")
  const { extname, basename } = await import("node:path")
  const { default: mime } = await import("mime")

  const type = mime.getType(extname(path))
  const blob = await openAsBlob(path, { type })
  const file = new File([blob], basename(path), { type: blob.type })

  const form = new FormData()
  form.append("file", file)

  const req = await fetch(new URL("my_files", api_url), {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: form,
  })

  const res = await req.json()
  return res
}

export async function importFile({
  api_url = URL_API,
  token,
  project_id,
  path,
}) {
  const req = await fetch(new URL(`file_import/${project_id}`, api_url), {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      source_path: path,
      // "taxo_mappings": {"23444": 76543},
      // "skip_loaded_files": False,
      // "skip_existing_objects": False,
      // "update_mode": "Yes",
    }),
  })

  const result = await req.json()
  return result
}
