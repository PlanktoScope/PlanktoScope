#!/usr/bin/env node

// https://github.com/sindresorhus/execa/blob/main/docs/bash.md

import chalk from "chalk"
import { $ } from "execa"
import input from "@inquirer/input"

function $verbose(cmd) {
  console.log(cmd)
}

console.log(
  "Setting up Git Identity",
  chalk.dim(
    "https://git-scm.com/book/ms/v2/Getting-Started-First-Time-Git-Setup#_your_identity",
  ),
)

let { stdout: user_name } = await $({
  reject: false,
})`git config --global user.name`
if (!user_name) {
  user_name = await input({
    message: `Please enter your name. ${chalk.dim(`e.g. John Doe`)}\n> `,
  })
  await $({ verbose: "short" })`git config --global user.name ${user_name}`
}

let { stdout: user_email } = await $({
  reject: false,
})`git config --global user.email`
if (!user_email) {
  user_email = await input({
    message: `Your email address? eg ${chalk.dim(`e.g. john.doe@example.edu`)}\n> `,
  })
  await $({ verbose: "short" })`git config --global user.email ${user_email}`
}

let { stdout: push_autoSetupRemote } = await $({
  reject: false,
})`git config --global push.autoSetupRemote`
if (!push_autoSetupRemote) {
  await $({ verbose: "short" })`git config --global push.autoSetupRemote true`
}
