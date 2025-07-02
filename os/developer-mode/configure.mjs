#!/usr/bin/env zx

console.log(
  "Setting up Git Identity",
  chalk.dim(
    "https://git-scm.com/book/ms/v2/Getting-Started-First-Time-Git-Setup#_your_identity"
  )
)

async function $verbose(...args) {
  $.verbose = true
  await $(...args)
  $.verbose = false
}

let user_name = String(await $`git config --global user.name`)
if (!user_name) {
  user_name = await question(
    `Please enter your name. ${chalk.dim(`e.g. John Doe`)}\n> `
  )
  await $verbose`git config --global user.name ${user_name}`
}

let user_email = String(await $`git config --global user.email`)
if (!user_email) {
  user_email = await question(
    `Your email address? eg ${chalk.dim(`e.g. john.doe@example.edu`)}\n> `
  )
  await $verbose`git config --global user.email ${user_email}`
}

if (!String(await $`git config --global push.autoSetupRemote`)) {
  await $verbose`git config --global push.autoSetupRemote true`
}
