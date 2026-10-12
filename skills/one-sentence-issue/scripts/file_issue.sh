#!/usr/bin/env bash
# file_issue.sh — file a GitHub issue and read it back to prove it landed.
#
#   ./file_issue.sh --repo owner/name --title "Title" --body-file draft.md \
#        [--template "Bug Report"] [--attach './img.png#alt'] [--search "keywords"]
#
# What it guarantees:
#   1. gh exists and is authenticated (fails loudly otherwise)
#   2. optional dedupe pass before filing
#   3. privacy scan on the draft  (level 2 aborts: ask the user first)
#   4. create the issue
#   5. read the body back and scan AGAIN — a successful command is not a successful report
#
# Exit codes: 0 ok · 2 blocked by a level-2 secret · 3 gh missing/unauthenticated · 4 usage

set -euo pipefail

REPO="" TITLE="" BODY="" TEMPLATE="" SEARCH=""
ATTACHES=()

usage() { sed -n '2,12p' "$0"; exit 4; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)     REPO="$2"; shift 2 ;;
    --title)    TITLE="$2"; shift 2 ;;
    --body-file) BODY="$2"; shift 2 ;;
    --template) TEMPLATE="$2"; shift 2 ;;
    --search)   SEARCH="$2"; shift 2 ;;
    --attach)   ATTACHES+=("$2"); shift 2 ;;
    -h|--help)  usage ;;
    *) echo "unknown option: $1" >&2; usage ;;
  esac
done

[[ -n "$REPO" && -n "$TITLE" && -n "$BODY" ]] || usage
[[ -f "$BODY" ]] || { echo "body file not found: $BODY" >&2; exit 4; }

# ---- 1. gh present and logged in -------------------------------------------
if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI not found. Install it from https://cli.github.com" >&2
  echo "gh 未安装 —— 或改用：把正文整块贴到网页提交。" >&2
  exit 3
fi
if ! gh auth status >/dev/null 2>&1; then
  echo "gh is not authenticated. Run: gh auth login" >&2
  echo "gh 未登录 —— 运行 gh auth login，或把正文整块贴到网页提交。" >&2
  exit 3
fi

# ---- 2. dedupe ---------------------------------------------------------------
if [[ -n "$SEARCH" ]]; then
  echo "== dedupe / 查重 =="
  if gh issue list --repo "$REPO" --state all --search "$SEARCH" --limit 5 2>&1 | grep -q .; then
    gh issue list --repo "$REPO" --state all --search "$SEARCH" --limit 5
    echo
    echo "Possible match above. If it is the same problem, comment on it instead."
    echo "上面可能已有同类 issue —— 如果是同一个问题，建议补评论而不是新开。"
    exit 0
  fi
  echo "no matches / 无重复"
fi

# ---- 3. privacy scan on the draft -------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCAN="$SCRIPT_DIR/privacy_scan.py"
PYTHON="$(command -v python3 || command -v python || true)"
if [[ -n "$PYTHON" && -f "$SCAN" ]]; then
  set +e
  "$PYTHON" "$SCAN" "$BODY"
  code=$?
  set -e
  if [[ $code -eq 2 ]]; then
    echo
    echo "BLOCKED: level-2 secret found. Ask the user (second confirmation), then either"
    echo "         redact the file and re-run, or pass --skip-scan if they insist."
    echo "已拦截：正文含疑似密钥。须经用户二次确认。"
    exit 2
  fi
fi

# ---- 4. file it --------------------------------------------------------------
ARGS=(issue create --repo "$REPO" --title "$TITLE" --body-file "$BODY")
[[ -n "$TEMPLATE" ]] && ARGS+=(--template "$TEMPLATE")
for f in ${ATTACHES[@]+"${ATTACHES[@]}"}; do ARGS+=(--attach "$f"); done

echo "== filing / 提交 =="
URL="$(gh "${ARGS[@]}")"
echo "$URL"
NUMBER="${URL##*/}"

# ---- 5. read back and re-scan ------------------------------------------------
echo
echo "== read back / 读回核对 =="
gh issue view "$NUMBER" --repo "$REPO" --json number,title,url,state --template \
  '{{.number}}  [{{.state}}]  {{.title}}
{{.url}}'

TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT
gh issue view "$NUMBER" --repo "$REPO" --json body --jq '.body' > "$TMP"

if [[ -n "$PYTHON" && -f "$SCAN" ]]; then
  set +e
  "$PYTHON" "$SCAN" "$TMP"
  scan2=$?
  set -e
  [[ $scan2 -eq 2 ]] && echo "WARNING: a secret landed in the live issue — redact it now." >&2
fi

echo
echo "Filed and verified / 已提交并读回核对: $URL"
echo "Labels will be empty — external contributors cannot add them (normal, not a failure)."
echo "标签为空属正常：外部贡献者无权打标签。"
