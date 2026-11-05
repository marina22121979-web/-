#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
remote_url='https://github.com/marina22121979-web/video-editing-skills.git'
python tools/build_catalog.py
if git remote get-url origin >/dev/null 2>&1; then
  actual_url="$(git remote get-url origin)"
  if [[ "$actual_url" != "$remote_url" ]]; then
    echo 'Origin points to a different repository; refusing to change it.' >&2
    exit 1
  fi
else
  git remote add origin "$remote_url"
fi
git push -u origin main
