#!/bin/zsh
# Runs once per new Conductor workspace, from the workspace root.
set -euo pipefail
export PATH="/opt/homebrew/bin:$PATH"

# Output folders point back to the main checkout, so results made in a
# workspace survive archiving it.
if [[ "${CONDUCTOR_IS_LOCAL:-}" == "1" && -n "${CONDUCTOR_ROOT_PATH:-}" ]]; then
  for dir in 02-vinted-watch/state 04-job-search/applications 04-job-search/state 05-content-machine/posts 06-match-predictor/data; do
    mkdir -p "$CONDUCTOR_ROOT_PATH/$dir"
    if [[ ! -e "$dir" ]]; then
      ln -s "$CONDUCTOR_ROOT_PATH/$dir" "$dir"
    fi
  done
fi

for ws in 02-vinted-watch 04-job-search 05-content-machine 06-match-predictor; do
  echo "== $ws"
  uv venv --quiet --allow-existing --python "$(command -v python3)" "$ws/.venv"
  uv pip install --quiet --python "$ws/.venv/bin/python" -r "$ws/requirements.txt"
done

05-content-machine/.venv/bin/playwright install chromium
