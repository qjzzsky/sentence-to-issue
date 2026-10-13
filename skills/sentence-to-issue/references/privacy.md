# Privacy: warn, then let the user decide

The default is **capture nothing sensitive and upload nothing on your own initiative**.
When something sensitive shows up, the user decides — you only inform.

## Two levels

| Level | What it is | Examples | What you do |
|---|---|---|---|
| **1 — identity / location / history** | things that identify or locate the user | username, local file paths, chat logs, session ids, email addresses, internal hostnames | Warn **once**, plainly. On yes, continue. |
| **2 — secrets** | things that unlock access | passwords, API keys, tokens, session cookies, private keys | **Second confirmation**: state the consequence first, then wait for an explicit reply. |

Content the user pasted themselves gets exactly the same warnings. Their text is not an
automatic consent to publish it.

### Wording (pick the user's language)

> **ZH (level 1):** 这段内容里可能有你的**个人信息**（用户名 / 本机路径 / 聊天记录）。要一起发上去吗？维护者排查通常不需要这些。
>
> **EN (level 1):** This draft may contain **personal details** (username / local paths / chat
> history). Include them? Maintainers rarely need them to reproduce the bug.

> **ZH (level 2):** ⚠️ 检测到**疑似密钥**（密码 / API key / token）。**一旦发出去就等于公开**，任何凭链接的人都能读到，且 GitHub issue 很难彻底删干净。
> 我建议抹掉它——通常维护者复现问题并不需要真的密钥。
> 要我抹掉，还是**你确认后照原样发**？
>
> **EN (level 2):** ⚠️ I found what looks like a **secret** (password / API key / token).
> Sending it makes it **public** — anyone with the link can read it, and GitHub issues are hard
> to fully erase. I'd recommend redacting it; maintainers rarely need a real credential to
> reproduce a bug. Redact it, or **confirm and send as-is**?

If the user insists after the warning, file it as they say. That is their call to make.

## What you never do on your own

- Never run a log-upload / debug-share command for them. That option exists only inside
  Step 7 of the flow, and only after they say yes to the question.
- Never broaden the capture beyond what the report needs.
- Never paste this repository's own internal notes, paths, or your session history into a report.

## The word list lives in the scanner

`scripts/privacy_scan.py` holds the detection patterns (placeholders, not real names).
Run it on the draft, run it again on what actually landed after filing, and act on its levels
using the table above.
