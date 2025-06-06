import { openAsBlob } from "node:fs"
import { extname, basename } from "node:path"

import mime from "mime"

export async function login({ api_url, username, password }) {
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

export async function uploadFile({ api_url, token, path }) {
  const type = mime.getType(extname(path))
  const blob = await openAsBlob(path, { type })
  const file = new File([blob], basename(path), { type: blob.type })

  const form = new FormData()
  form.append("file", file)

  const req = await fetch(new URL("my_files/", api_url), {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: form,
  })
  const res = await req.json()
  return res
}

export async function importFile({ api_url, token, project_id, path }) {
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
