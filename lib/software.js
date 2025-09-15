import { $ } from "execa"
import git from "isomorphic-git"
import fs from "fs"

import { cache } from "./helpers.js"

const getRoot = cache(() => git.findRoot({ fs, filepath: import.meta.dirname }))

export async function getSoftwareVersion() {
  const { stdout: described } = await $({
    cwd: await getRoot(),
  })`git describe --tags --match software/v* --dirty --broken`
  return described.split("software/")[1]
}

async function getUrl() {
  const dir = await getRoot()

  const [remotes, branch] = await Promise.all([
    git.listRemotes({ fs, dir }),
    git.currentBranch({
      fs,
      dir,
      test: true,
    }),
  ])

  if (!branch) return remotes[0]?.url

  const remote = await git.getConfig({
    fs,
    dir,
    path: `branch.${branch}.remote`,
  })

  return remotes.find((item) => item.remote === remote)?.url
}

async function getCommit() {
  const logs = await git.log({
    fs,
    dir: await getRoot(),
    depth: 1,
  })
  return logs[0].oid
}

export async function getSoftwareVersioning() {
  const [commit, url, version] = await Promise.all([
    getCommit(),
    getUrl(),
    getSoftwareVersion(),
  ])

  return {
    repo: url,
    commit,
    version,
  }
}
