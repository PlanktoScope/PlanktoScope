import { test } from "node:test"
import { getSoftwareVersion, getSoftwareVersioning } from "./software.js"
import { $ } from "execa"

test("getSoftwareVersion", async (t) => {
  const version = await getSoftwareVersion()

  t.assert.deepStrictEqual(
    version,

    (
      await $`git describe --tags --match software/v* --dirty --broken`
    ).stdout.split("software/")[1],
  )
})

test("getSoftwareVersioning", async (t) => {
  const info = await getSoftwareVersioning()

  t.assert.deepStrictEqual(info, {
    repo: (await $`git config --get remote.origin.url`).stdout,
    commit: (await $`git rev-parse HEAD`).stdout,
    version: (
      await $`git describe --tags --match software/v* --dirty --broken`
    ).stdout.split("software/")[1],
  })
})
