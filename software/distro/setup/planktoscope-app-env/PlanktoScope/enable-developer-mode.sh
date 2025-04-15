#!/bin/bash -eux

repo=$HOME/PlanktoScope
cd $repo
git init
git remote add origin git@github.com:PlanktoScope/PlanktoScope.git
git fetch origin --filter=blob:none
git reset origin/HEAD
