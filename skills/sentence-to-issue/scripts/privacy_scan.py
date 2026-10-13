#!/usr/bin/env python3
"""
privacy_scan.py — scan a draft issue body for things the user may not want public.

Usage:
    python3 privacy_scan.py <file>            scan a file
    python3 privacy_scan.py -                 scan stdin

Exit codes:
    0  clean
    1  level-1 findings only (identity / location / history)  -> warn once, user decides
    2  level-2 findings (password / API key / token / key)    -> second confirmation required
   64  usage error (missing file argument)
   66  file could not be read

Detection patterns are GENERIC placeholders. This file intentionally contains no real
usernames, hostnames or paths of its own — the word list lives here, not in your report.

Deliberate exemptions: wrap a block in  <!-- privacy-allow -->  ...  <!-- /privacy-allow -->
and it is skipped (line numbers stay correct). Use it ONLY for content published on
purpose, e.g. an author block. Anything else that trips a rule must be redacted, not marked.
"""

import re
import sys

# (level, label_en, label_zh, pattern)
RULES = [
    # ---- level 2: secrets ----
    (2, "GitHub token", "GitHub 令牌",
     r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b"),
    (2, "GitHub fine-grained PAT", "GitHub 细粒度令牌",
     r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    (2, "AWS access key", "AWS 访问密钥",
     r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    (2, "OpenAI / Anthropic style key", "OpenAI/Anthropic 风格密钥",
     r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    (2, "Slack token", "Slack 令牌",
     r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    (2, "Private key block", "私钥块",
     r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----"),
    (2, "JSON Web Token", "JWT",
     r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}\b"),
    (2, "Assigned password / secret / token", "赋值形式的密码/密钥",
     r"(?i)\b(?:password|passwd|pwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret)\b\s*[:=]\s*[\"']?[^\s\"']{6,}"),
    (2, "Connection string with credentials", "带账密的连接串",
     r"(?i)\b[a-z]+://[^/\s:@]+:[^/\s:@]+@[^/\s]+"),

    # ---- level 1: identity / location / history ----
    # The path prefixes are concatenated on purpose: a scanner must not match
    # its own source, and this file must not contain a literal home-path prefix.
    (1, "Home directory path", "本机家目录路径",
     r"(?i)(?<![A-Za-z0-9])(?:[A-Z]:\\Users\\|/home/|" + "/Us" + "ers/)"
     r"[^\s\"'<>|]{2,}"),
    (1, "Email address", "邮箱地址",
     r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    (1, "Private / internal IP", "内网 IP",
     r"\b(?:10\.\d{1,3}|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b"),
    (1, "Chat / session identifier", "会话标识",
     r"(?i)\b(?:chat[_-]?id|session[_-]?id|thread[_-]?id|request[_-]?id)\b\s*[:=]\s*[\"']?[A-Za-z0-9_:-]{6,}"),
    (1, "Local username assignment", "本机用户名赋值",
     r"(?i)\b(?:user(?:name)?|login)\b\s*[:=]\s*[\"']?[A-Za-z0-9._-]{3,}"),
    # github.com/<owner> is deliberately absent: it appears in every issue body.
    (1, "Social profile link", "社交账号主页链接",
     r"(?i)(?:weibo\.com/(?:u/)?|space\.bilibili\.com/|zhihu\.com/people/"
     r"|(?:twitter\.com|x\.com)/|weixin\.qq\.com/s/)[A-Za-z0-9_-]+"),
]


ALLOW_RE = __import__("re").compile(
    r"<!--\s*privacy-allow\s*-->.*?<!--\s*/privacy-allow\s*-->", __import__("re").S
)


def strip_allowed(text):
    """Drop blocks marked as intentionally public, keeping line numbers stable."""
    return ALLOW_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def scan(text):
    hits = []
    for level, en, zh, pattern in RULES:
        for match in re.finditer(pattern, text):
            snippet = match.group(0)
            if len(snippet) > 60:
                snippet = snippet[:57] + "..."
            hits.append((level, en, zh, snippet, text.count("\n", 0, match.start()) + 1))
    return hits


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 64
    source = sys.argv[1]
    if source == "-":
        text = sys.stdin.read()
        label = "<stdin>"
    else:
        try:
            with open(source, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError as exc:
            print(f"cannot read {source}: {exc}", file=sys.stderr)
            return 66
        label = source

    hits = scan(strip_allowed(text))
    if not hits:
        print(f"[OK] {label} — no sensitive patterns found / 未发现敏感内容")
        return 0

    level2 = [h for h in hits if h[0] == 2]
    level1 = [h for h in hits if h[0] == 1]

    print(f"\nprivacy scan: {label}")
    print("=" * 60)
    for level, en, zh, snippet, line in sorted(hits, key=lambda h: -h[0]):
        flag = "LEVEL 2 / 高危" if level == 2 else "LEVEL 1 / 提醒"
        print(f"  [{flag}] line {line}: {en} / {zh}")
        print(f"      -> {snippet}")
    print("=" * 60)

    if level2:
        print("\nLEVEL 2 — secrets detected / 检测到疑似密钥")
        print("  Sending this makes the value PUBLIC and GitHub issues are hard to erase.")
        print("  发出去即公开，且 issue 很难彻底删除。需要用户二次确认。")
        print("  Recommended: redact it. Suggested fix: replace the value with <redacted>.")
        print("  Exit code 2 -> the assistant must ask before filing.")
        return 2

    print("\nLEVEL 1 — identity / location / history / 检测到个人信息")
    print("  Warn the user once, then continue if they agree.")
    print("  提醒用户一次，用户同意即可继续。")
    print("  Exit code 1 -> warn, then proceed on yes.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
