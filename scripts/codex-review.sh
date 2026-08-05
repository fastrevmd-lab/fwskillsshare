#!/usr/bin/env bash
# Run the Codex review gate against a commit, with the superpowers skill
# temporarily off the Codex skill path.
#
# Why: ~/.agents/skills/superpowers is a symlink into ~/.codex/superpowers/skills,
# so Codex discovers it as a skill on every run — including `codex exec review`.
# Its "you ABSOLUTELY MUST invoke the skill" preamble makes the reviewer read
# skill files and attempt subagent dispatch instead of reading the diff. Seven
# runs in a row ended with no final agent_message. With the symlink moved aside
# and nothing else changed, the same command on the same commit returned a
# complete review in under eight minutes.
#
# Usage:
#   scripts/codex-review.sh                 # review HEAD
#   scripts/codex-review.sh <sha>           # review a specific commit
#   scripts/codex-review.sh --base main     # review a branch against a base
#
# Exit status: 0 if a verdict was produced, 1 if the gate did not run.
# A gate that produces no verdict is NOT a pass — this script says so and fails.
set -uo pipefail

LINK="${CODEX_SKILLS_DIR:-$HOME/.agents/skills}/superpowers"
PARKED="$LINK.gate-parked"
OUT="$(mktemp -t codex-review-XXXXXX.jsonl)"

restore() {
  if [ -e "$PARKED" ]; then
    mv "$PARKED" "$LINK"
  fi
}
trap restore EXIT INT TERM

if [ $# -eq 0 ]; then
  set -- "$(git rev-parse HEAD)"
fi

case "$1" in
  --base) SCOPE=(--base "$2") ;;
  *)      SCOPE=(--commit "$1") ;;
esac

# Neither --commit nor --base accepts a custom prompt; the CLI rejects the
# combination. Scoping therefore has to come from commit size, not instructions.
if [ -e "$LINK" ]; then
  # Fail closed. If parking does not succeed the review would silently run with
  # the skill still active — the exact condition this wrapper exists to avoid.
  if ! mv "$LINK" "$PARKED"; then
    echo "ERROR: could not park $LINK — refusing to run an unmitigated review." >&2
    exit 1
  fi
  echo "superpowers parked for the duration of this review" >&2
fi

echo "reviewing: ${SCOPE[*]}" >&2
# Keep stderr: when codex cannot start (auth, config, a rejected argument) that
# message is the only diagnostic, and the JSON stream will be empty. It must not
# be merged into $OUT — one non-JSON line there would break the verdict parse.
ERR="${OUT%.jsonl}.err"
timeout "${CODEX_REVIEW_TIMEOUT:-600}" \
  codex exec review "${SCOPE[@]}" --json >"$OUT" 2>"$ERR"

# The verdict is the final agent_message. `fromjson?` rather than plain jq: one
# stray non-JSON line would abort a strict parse and lose the whole review.
VERDICT="$(jq -rR 'fromjson? | select(.type=="item.completed") | .item
                   | select(.type=="agent_message") | .text' "$OUT" 2>/dev/null)"

if [ -z "$VERDICT" ]; then
  echo >&2
  echo "GATE DID NOT RUN — no final agent_message in $(wc -l <"$OUT") events." >&2
  echo "Do not treat this as a pass. Raw output: $OUT" >&2
  if [ -s "$ERR" ]; then
    echo "stderr ($ERR):" >&2
    head -5 "$ERR" >&2
  fi
  exit 1
fi

echo
echo "$VERDICT"
echo
if printf '%s' "$VERDICT" | grep -qE '\[P0\]|\[P1\]'; then
  echo "BLOCKING findings present ([P0]/[P1]) — fix before merging." >&2
  echo "Raw output: $OUT" >&2
  exit 1
fi
echo "No [P0]/[P1] findings. Raw output: $OUT" >&2
