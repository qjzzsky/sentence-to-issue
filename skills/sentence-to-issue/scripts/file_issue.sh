#!/usr/bin/env bash
# file_issue.sh — file a GitHub issue and read it back to prove it landed.
#
#   ./file_issue.sh --repo owner/name --title "Title" --body-file draft.md \
#        [--attach './img.png#alt'] [--search "keywords"]
#        [--allow '<authorised value>']... [--skip-scan]
#
# --allow: authorise ONE exact literal (repeatable) that the target repo asked
#          for and the user signed off on. PREFER THIS over --skip-scan, which
#          turns the scanner off for the WHOLE draft and is a last resort.
#
# --attach: the path must match the reference in the body character for character
#           (e.g. body has ![alt](./img.png) -> pass './img.png#alt'). A mismatched
#           path makes gh append a second copy instead of rewriting the reference.
#
# NOTE: there is deliberately NO --template flag. gh refuses --template together
#       with --body-file, so fold the repository template into the draft first.
#
# What it guarantees:
#   1. gh exists and is authenticated (fails loudly otherwise)
#   2. optional dedupe - a failed query aborts instead of reading as no-match
#   3. privacy scan on the draft  (level 2 aborts: ask the user first)
#   4. create the issue
#   5. read the body back and scan AGAIN — a successful command is not a successful report
#
# Exit codes: 0 ok · 1 gh itself failed (repo missing / no permission / rate limited —
#             passed through as-is) · 2 blocked by a level-2 secret
#             3 gh missing/unauthenticated · 4 usage error · 5 dedupe query failed
#             6 unexpected output from gh create · 7 privacy scanner failed to run

set -euo pipefail

# git-bash/MSYS hands POSIX drive paths (/e/...) to a native Windows Python, which
# reads them as C:\e\... and fails. This normalises drive paths ONLY; /tmp and /home
# are real POSIX locations with no Windows equivalent, so nothing creates files there
# (temp output goes through variables and pipes instead of mktemp).
native() {
  case "$1" in
    /[A-Za-z]/*) printf '%s' "$1" | sed -E 's|^/([A-Za-z])/|\1:/|' ;;
    *) printf '%s' "$1" ;;
  esac
}

REPO="" TITLE="" BODY="" SEARCH="" SKIP_SCAN=0
ALLOWS=()
ATTACHES=()

usage() { sed -n '2,24p' "$0"; exit 4; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)     REPO="$2"; shift 2 ;;
    --title)    TITLE="$2"; shift 2 ;;
    --body-file) BODY="$2"; shift 2 ;;
    --search)    SEARCH="$2"; shift 2 ;;
    --attach)    ATTACHES+=("$2"); shift 2 ;;
    --allow)     ALLOWS+=("$2"); shift 2 ;;
    --skip-scan) SKIP_SCAN=1; shift ;;
    -h|--help)   usage ;;
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
  set +e
  OUT="$(gh issue list --repo "$REPO" --state all --search "$SEARCH" --limit 5 2>&1)"
  QC=$?
  set -e
  if [[ $QC -ne 0 ]]; then
    echo "dedupe query failed (exit $QC) - NOT reading this as no-match." >&2
    echo "查重查询失败，不会当成「无重复」继续提交。原始输出：" >&2
    printf '%s\n' "$OUT" | sed 's/^/  /' >&2
    exit 5
  fi
  if [[ -n "$OUT" ]]; then
    echo "$OUT"
    echo
    echo "Possible match above. If it is the same problem, comment on it instead."
    echo "上面可能已有同类 issue —— 如果是同一个问题，建议补评论而不是新开。"
    exit 0
  fi
  echo "no matches / 无重复"
fi

# ---- 3. privacy scan on the draft -------------------------------------------
SCRIPT_DIR="$(native "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)")"
SCAN="$SCRIPT_DIR/privacy_scan.py"
PYTHON="$(command -v python3 || command -v python || true)"
if [[ $SKIP_SCAN -eq 1 ]]; then
  echo
  echo "!! privacy scan SKIPPED by --skip-scan - filing unchecked."
  echo "!! 已按 --skip-scan 跳过隐私扫描 —— 正文未经检查。"
elif [[ -n "$PYTHON" && -f "$SCAN" ]]; then
  set +e
  SCAN_OUT="$("$PYTHON" "$SCAN" "$BODY" ${ALLWS[@]+"${ALLWS[@]}"} 2>&1)"
  code=$?
  set -e
  printf '%s\n' "$SCAN_OUT"
  if [[ $code -eq 2 && "$SCAN_OUT" == *"LEVEL 2"* ]]; then
    echo
    echo "BLOCKED: level-2 secret found."
    echo "  MAIN PATH: redact that spot in the draft, then re-run."
    echo "  EXCEPTION: only if the target repo demands it AND the user authorised"
    echo "             that exact value -> re-run with --allow '<the value>'."
    echo "  LAST RESORT: --skip-scan turns the scanner off for the WHOLE draft."
    echo "主路：把这一处脱敏后重跑。"
    echo "例外：仅当目标仓库明确要求、且用户已对那一处授权 —— 用 --allow '<该值>' 重跑。"
    echo "最后手段：--skip-scan 是整份不扫。"
    exit 2
  elif [[ $code -ne 0 && "$SCAN_OUT" != *"LEVEL"* ]]; then
    echo "privacy scanner itself failed (exit $code) - refusing to file unchecked." >&2
    echo "隐私扫描器没能运行 —— 不提交未经检查的正文。" >&2
    exit 7
  fi
fi

# ---- 4. file it --------------------------------------------------------------
ARGS=(issue create --repo "$REPO" --title "$TITLE" --body-file "$BODY")
for f in ${ATTACHES[@]+"${ATTACHES[@]}"}; do ARGS+=(--attach "$f"); done

echo "== filing / 提交 =="
URL="$(gh "${ARGS[@]}")"

# gh prints one URL; anything else would corrupt the number parsed below.
if [[ ! "$URL" =~ ^https://github\.com/[^/]+/[^/]+/issues/[0-9]+$ ]]; then
  echo "unexpected output from gh issue create, refusing to parse a number:" >&2
  printf '%s\n' "$URL" >&2
  exit 6
fi
echo "$URL"
NUMBER="${URL##*/}"

# ---- 5. read back and re-scan ------------------------------------------------
echo
echo "== read back / 读回核对 =="
gh issue view "$NUMBER" --repo "$REPO" --json number,title,url,state --template \
  '{{.number}}  [{{.state}}]  {{.title}}
{{.url}}'

if [[ $SKIP_SCAN -eq 0 && -n "$PYTHON" && -f "$SCAN" ]]; then
  LIVE="$(gh issue view "$NUMBER" --repo "$REPO" --json body --jq '.body')"
  set +e
  SCAN2_OUT="$(printf '%s' "$LIVE" | "$PYTHON" "$SCAN" - ${ALLWS[@]+"${ALLWS[@]}"} 2>&1)"
  scan2=$?
  set -e
  printf '%s\n' "$SCAN2_OUT"
  if [[ $scan2 -eq 2 && "$SCAN2_OUT" == *"LEVEL 2"* ]]; then
    echo "WARNING: a secret landed in the live issue - redact it now." >&2
  elif [[ $scan2 -ne 0 && "$SCAN2_OUT" != *"LEVEL"* ]]; then
    echo "WARNING: privacy scanner failed on the read-back (exit $scan2)." >&2
  fi
fi

echo
# --skip-scan means neither the draft nor the live body was ever scanned;
# claiming "verified" there would overstate what actually happened.
if [[ $SKIP_SCAN -eq 1 ]]; then
  echo "Filed (privacy scan SKIPPED / 未扫，未复扫): $URL"
else
  echo "Filed and verified / 已提交并读回核对: $URL"
fi
echo "Labels are empty because this flow never passes --label (normal, not a failure)."
echo "标签为空属正常：本流程不传 --label。"
