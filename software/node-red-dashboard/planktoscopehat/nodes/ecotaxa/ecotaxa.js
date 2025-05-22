const { openAsBlob } = require("node:fs")
const { extname, basename } = require("node:path")

const { default: mime } = require("mime")

module.exports = function (RED) {
  function EcotaxaNode(config) {
    RED.nodes.createNode(this, config)
    const node = this
    const { username, password } = node.credentials
    node.on("input", function (msg, send, done) {
      const { file_path } = msg.payload
      const { api_url, project_id } = config
      go({ api_url, project_id, username, password, file_path })
        .then((result) => {
          msg.payload = result
          send(msg)
          done()
        })
        .catch((err) => {
          done(err)
        })
    })
  }
  RED.nodes.registerType("ecotaxa", EcotaxaNode, {
    credentials: {
      username: { type: "text" },
      password: { type: "password" },
    },
  })
}

async function go({ api_url, username, password, project_id, file_path }) {
  const token = await login({ api_url, username, password })

  const remote_path = await uploadFile({
    api_url,
    path: file_path,
    token,
  })

  const result = await importFile({
    api_url,
    path: remote_path,
    project_id,
    token,
  })

  return result
}

async function login({ api_url, username, password }) {
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

async function uploadFile({ api_url, token, path }) {
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

async function importFile({ api_url, token, project_id, path }) {
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
