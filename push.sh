#!/bin/bash
set -e
export HOME=/root/.hermes/profiles/banksy/home
export GIT_TERMINAL_PROMPT=0
cd /root/ib-landing

if [ ! -d .git ]; then
  git init -q
  git symbolic-ref HEAD refs/heads/main
fi
git config user.name "Banksy (Dal's agent)"
git config user.email "darrenhopwood13@gmail.com"

git add index.html README.md .gitignore
git status --short
git commit -q -m "instructBrain landing page redesign - standalone mockup" || echo "(nothing to commit)"

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin https://github.com/darrenhopwood13-maker/ib-landing.git
else
  git remote add origin https://github.com/darrenhopwood13-maker/ib-landing.git
fi
git push -u origin main
echo "PUSH OK"
git log --oneline -n 3
git ls-remote origin | head
