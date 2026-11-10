#!/usr/bin/env bash
# Connect Feishu with the USER's own identity in a fresh cloud session.
#
#   bash scripts/feishu-login.sh          # step 1: prints an authorization link
#   bash scripts/feishu-login.sh wait     # step 2: blocks until the user clicks 授权
#
# Needs FEISHU_APP_ID / FEISHU_APP_SECRET in the environment.
# After that: npx -y @larksuite/cli@1.0.98 <command> --as user
set -euo pipefail

CLI="npx -y @larksuite/cli@1.0.98"
STATE="${TMPDIR:-/tmp}/feishu-device.json"

: "${FEISHU_APP_ID:?FEISHU_APP_ID not set}"
: "${FEISHU_APP_SECRET:?FEISHU_APP_SECRET not set}"

if [ "${1:-}" = "wait" ]; then
  dc=$(node -e 'console.log(JSON.parse(require("fs").readFileSync(process.argv[1])).device_code)' "$STATE")
  $CLI auth login --device-code "$dc" --json >/dev/null 2>&1 || true
  $CLI auth status 2>/dev/null | grep -E '"(userName|tokenStatus)"' | head -2
  exit 0
fi

# Configure app credentials (secret via stdin, never on the command line).
if ! $CLI auth status >/dev/null 2>&1; then
  printf '%s' "$FEISHU_APP_SECRET" | $CLI config init --app-id "$FEISHU_APP_ID" --app-secret-stdin --brand feishu --lang zh >/dev/null
fi

$CLI auth login --recommend --no-wait --json > "$STATE" 2>/dev/null
url=$(node -e 'console.log(JSON.parse(require("fs").readFileSync(process.argv[1])).verification_url)' "$STATE")
echo "请用户打开并点「授权」（10 分钟内有效）："
echo "$url"
echo "然后运行: bash scripts/feishu-login.sh wait"
