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
and it is skipped for LEVEL-1 rules ONLY (line numbers stay correct, and every scan prints
a "[skip] N lines exempted ..." line saying exactly what was passed over). LEVEL-2 secrets
are NEVER exempt: a password, token or private key inside such a block is still reported on
the raw text and still demands the second confirmation. Use the marker ONLY for content
published on purpose, e.g. an author block; anything else that trips a rule must be redacted,
not marked.

LEVEL-2 scans THREE views of the same text, because GitHub hides HTML comments and readers
copy values out across line breaks: the raw text, the text with all HTML comments deleted
(what a reader actually sees), and the text with newlines joined. A hit that only appears
in a rebuilt view prints a line number like `~3 [uncommented]` — approximate on purpose;
the exit code 2 gate is what matters, not the exact line.

THIS SCANNER IS HEURISTIC, NOT PROOF. A secret split or obfuscated in a way these views
don't reconstruct can still slip through. The last line of defence is Step 10: the user
reads the full body before anything is filed.
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
     r"|(?:twitter\.com|x\.com)/|weixin\.qq\.com/s/|t\.me/|gitee\.com/"
     r"|xiaohongshu\.com/user/profile/|douyin\.com/user/|juejin\.cn/user/"
     r"|douban\.com/people/|linkedin\.com/in/|reddit\.com/user/"
     r"|bsky\.app/profile/)"
     r"[A-Za-z0-9_-]+"),
]


ALLOW_RE = re.compile(
    r"<!--\s*privacy-allow\s*-->.*?<!--\s*/privacy-allow\s*-->", re.S
)


def allow_blocks(text):
    """Every exempted span as (start_line, end_line, line_count)."""
    out = []
    for m in ALLOW_RE.finditer(text):
        start = text.count("\n", 0, m.start()) + 1
        end = text.count("\n", 0, m.end()) + 1
        out.append((start, end, end - start + 1))
    return out


def strip_allowed(text):
    """Blank out blocks marked as intentionally public.

    Non-newline characters become spaces (length and line breaks preserved),
    so boundary characters on either side of the marker can never be spliced
    together into a hit that does not exist in the file."""
    return ALLOW_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
NEWLINE_RE = re.compile(r"[ \t]*\r?\n[ \t]*")


def _views(text):
    """The text forms level-2 must be checked against.

    GitHub hides HTML comments, so `ghp_AB<!-- x -->CD` renders as one
    continuous token; a reader copying a token out of a wrapped block also
    ignores the line break. Rebuilding both forms catches what the raw-text
    pass cannot. The raw text comes first so exact line numbers win.
    """
    yield None, text                                    # exact line numbers
    yield "uncommented", COMMENT_RE.sub("", text)      # what the reader sees
    yield "newline-joined", NEWLINE_RE.sub("", text)   # values wrapped mid-token


def _locate(text, snippet):
    """Line of the snippet in the raw text; falls back to its first 12 chars
    (the hit was reconstructed, so the exact string may not exist verbatim)."""
    i = text.find(snippet)
    if i < 0:
        i = text.find(snippet[:12])
    if i < 0:
        return "~?", True
    return text.count("\n", 0, i) + 1, True


def scan(text):
    """Level-2 rules run on the raw text AND on the rebuilt views above —
    the marker can only excuse identity findings, never a secret, and a secret
    cut apart by a comment or a line break still counts. Level-1 rules run on
    the text with exempted spans blanked: non-newline characters are replaced
    by spaces (length and line breaks preserved), so line numbers stay
    identical and boundary characters can never be spliced into a fake hit.
    Reconstructed hits print an approximate line marked with its view."""
    hits = []
    seen = set()
    level1_text = strip_allowed(text)

    for level, en, zh, pattern in RULES:
        views = [(None, level1_text)] if level == 1 else list(_views(text))
        for label, haystack in views:
            for match in re.finditer(pattern, haystack):
                snippet = match.group(0)
                if len(snippet) > 60:
                    snippet = snippet[:57] + "..."
                key = (level, snippet)
                if key in seen:
                    continue
                seen.add(key)
                if label is None:
                    line = haystack.count("\n", 0, match.start()) + 1
                    line_str = str(line)
                else:
                    line, _ = _locate(text, snippet)
                    line_str = f"~{line} [{label}]"
                hits.append((level, en, zh, snippet, line_str))
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

    # The marker never hides anything from level 2; it only excuses level 1,
    # and whatever it skipped is printed so the reader can see it happened.
    for start, end, n in allow_blocks(text):
        print(f"[skip] {n} lines exempted by an inline marker (line {start}-{end})")

    hits = scan(text)
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
