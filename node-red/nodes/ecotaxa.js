import { login, uploadFile, importFile } from "./api/ecotaxa.js"

export default function (RED) {
  function Node(config) {
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
  RED.nodes.registerType("ecotaxa", Node, {
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
