import { $ } from "execa"
import git from "isomorphic-git"
import fs from "fs"

const dir = "/home/pi/PlanktoScope"

export async function getSoftwareVersion() {
  const { stdout: described } =
    await $`git describe --tags --match software/v* --dirty --broken`
  return described.split("software/")[1]
}

async function getUrl() {
  const branch = await git.currentBranch({
    fs,
    dir,
    test: true,
  })
  const remote = await git.getConfig({
    fs,
    dir,
    path: `branch.${branch}.remote`,
  })
  const url = await git.getConfig({
    fs,
    dir,
    path: `remote.${remote}.url`,
  })
  return url
}

async function getCommit() {
  const logs = await git.log({
    fs,
    dir,
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
