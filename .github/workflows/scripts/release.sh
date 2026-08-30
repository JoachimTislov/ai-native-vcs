#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <major.minor.patch>" >&2
  exit 1
fi

version="$1"
if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Version must use semantic versioning: X.Y.Z" >&2
  exit 1
fi

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

python -m pytest tests -q
python - <<PY "$version"
from pathlib import Path
import re
import sys

version = sys.argv[1]
path = Path('pyproject.toml')
text = path.read_text()
text, count = re.subn(r'(?m)^version = ".*?"$', f'version = "{version}"', text)
if count == 0:
    raise SystemExit('No version field found in pyproject.toml')
path.write_text(text)
PY

git add pyproject.toml

git commit -m "Release v${version}"

git tag -a "v${version}" -m "Release v${version}"

git push origin HEAD --follow-tags

echo "Released v${version}"
