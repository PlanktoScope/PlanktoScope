#!/usr/bin/env node

// https://github.com/sindresorhus/execa/blob/main/docs/bash.md

import { styleText } from "node:util"
import { $ } from "execa"
import input from "@inquirer/input"

console.log(
  "Setting up Git Identity",
  styleText(
    "dim",
    "https://git-scm.com/book/ms/v2/Getting-Started-First-Time-Git-Setup#_your_identity",
  ),
)

let { stdout: user_name } = await $({
  reject: false,
})`git config --global user.name`
if (!user_name) {
  user_name = await input({
    message: `Please enter your name. ${styleText("dim", `e.g. John Doe`)}\n> `,
  })
  await $`git config --global user.name ${user_name}`
}

let { stdout: user_email } = await $({
  reject: false,
})`git config --global user.email`
if (!user_email) {
  user_email = await input({
    message: `Your email address? eg ${styleText("dim", `e.g. john.doe@example.edu`)}\n> `,
  })
  await $`git config --global user.email ${user_email}`
}

let { stdout: push_autoSetupRemote } = await $({
  reject: false,
})`git config --global push.autoSetupRemote`
if (!push_autoSetupRemote) {
  await $`git config --global push.autoSetupRemote true`
}
