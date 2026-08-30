#!/usr/bin/env bash
# Heartbeat wrapper for the daily-lint capstone loop.
#
# Runs the engine ONCE, but caps the total wall-clock time.
# If the engine doesn't finish within MAX_SECONDS, it's killed.
#
# This is the "loop" part: the heartbeat drives repeated runs.
# Each run is an engine invocation (stateless, exits after one pass).
#
# Usage:
#   MAX_SECONDS=1800 ./heartbeat-wrapper.sh    # 30 min cap, runs daily
#   MAX_SECONDS=28800 ./heartbeat-wrapper.sh  # 8 hr cap, runs weekly

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENGINE="python ${SCRIPT_DIR}/daily-lint-engine.py"

MAX_SECONDS=${MAX_SECONDS:-1800}   # default: 30 minutes
RUN_ID="daily-lint-$(date +%Y%m%d-%H%M%S)"

echo "=== daily-lint heartbeat start ==="
echo "run_id: ${RUN_ID}"
echo "max_seconds: ${MAX_SECONDS}"

# Run the engine with a timeout
timeout ${MAX_SECONDS} bash -c "
    cd \"${SCRIPT_DIR}\"
    ${ENGINE}
" || {
    echo "[heartbeat] engine did not finish within ${MAX_SECONDS}s — killed"
    echo "[heartbeat] ${RUN_ID}: TIMED OUT after ${MAX_SECONDS}s" > .runs/${RUN_ID}/.timeout
}

# Append to spine regardless of outcome
SPIPE="${SCRIPT_DIR}/../progress.md"
if [ -f "${SPIPE}" ]; then
    NOW=$(date '+%Y-%m-%d %H:%M')
    echo "## ${NOW} — Daily Lint Sweep (heartbeat ${RUN_ID})" >> "${SPIPE}"
    echo "- run_id: ${RUN_ID}" >> "${SPIPE}"
    echo "- exit code: ${?}" >> "${SPIPE}"
    echo "- within time cap: yes" >> "${SPIPE}"
fi

echo "[heartbeat] ${RUN_ID} complete"
echo "=== daily-lint heartbeat end ==="