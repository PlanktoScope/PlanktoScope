const { openAsBlob } = require("node:fs")
const { extname, basename } = require("node:path")

const { default: mime } = require("mime")

module.exports = function (RED) {
  function EcotaxaNode(config) {
    // console.log(config)
    RED.nodes.createNode(this, config)
    var node = this
    node.on("input", function (msg) {
      msg.payload = msg.payload.toLowerCase()
      node.send(msg)
    })
  }
  RED.nodes.registerType("ecotaxa", EcotaxaNode)
}

const ecotaxa_api_url = "http://192.168.1.128:8088/api/"

;(async () => {
  const token = await login()

  const foo = await uploadFile({
    path: "/home/pi/PlanktoScope/config.json",
    token,
  })

  console.log(foo)
})()

async function login() {
  const req = await fetch(new URL("login", ecotaxa_api_url), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username: "administrator", password: "ecotaxa" }),
  })
  const token = await req.json()
  return token
}

async function createProject({ token }) {
  const req = await fetch(new URL("projects/create", ecotaxa_api_url), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      // "clone_of_id": 2,
      title: "My new project title",
      // "instrument": "PlanktoScope test",
      // "visible": True,
    }),
  })
  const project_id = await req.json()
  return project_id
}

async function uploadFile({ path, token }) {
  const type = mime.getType(extname(path))
  const blob = await openAsBlob(path, { type })
  const file = new File([blob], basename(path), { type: blob.type })

  const form = new FormData()
  form.append("file", file)

  const req = await fetch(new URL("my_files", ecotaxa_api_url), {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    // body: form,
  })
  const res = await req.json()
  return res
}

async function importFile({ path, project_id, token }) {
  const req = await fetch(
    new URL(`file_import/${project_id}`, ecotaxa_api_url),
    {
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
    }
  )

  const result = await req.json()
  const job_id = result["job_id"]
  return job_id
}
