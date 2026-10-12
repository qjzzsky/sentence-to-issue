---
name: one-sentence-issue
description: >-
  Use when the user says "file an issue", "report this bug to the repo",
  "one sentence issue", or the Chinese equivalents "一句话提 GitHub issue" /
  "帮我把这个 bug 传上去" - turn one sentence of description into a filed GitHub
  issue on any public repository. Gathers evidence, privacy-checks the draft,
  writes the report, submits with the gh CLI, then reads it back to verify.
  Works for any software or game, not only AI tools.
license: MIT
---

# One-Sentence Issue · 一句话提 GitHub issue

Turn one sentence about something broken into a filed GitHub issue — and hand the user the link.

The user is not a developer by default. Explain in plain language, keep it short, and never
assume they know GitHub vocabulary.

---

## Language rules (hard)

1. **Reply in the language the user writes in.** Chinese in → Chinese out. English in → English out.
2. **The issue body follows the target repository's language** — check its README / recent issues.
   English open-source project → English body. Default to English when unsure.
3. **This file and `references/` are for you, not for the user.** Never paste them into the chat.
   Lines marked `ZH:` / `EN:` are user-facing scripts — pick the one matching the user's language.

---

## The flow (12 steps)

### 1. Parse the one sentence
Extract three things: **what broke**, **which repository**, **what evidence the user already has**.
Ask only for what is missing. Never guess the repository.

### 2. Resolve the target repository — exactly two sources
1. `git remote get-url origin` in the current working directory
2. The user's own words: an `owner/repo`, or a full `https://github.com/...` link

There is **no keyword search** — if neither source yields a repository, ask the user for it.

### 3. Capability probe
Inventory what you can actually reach: terminal, file read, browser, screenshots, installed skills.
That decides how deep you can capture (see `references/evidence.md`). Chat window only → layer L0.
**Never invent evidence you did not read.**

### 4. Freeze the scene — say this first, in the user's language
> **ZH:** **正在搜集相关信息 —— 期间别刷新、别重启、别更新、别关窗口。** 这期间如果你有与 bug 相关的细节要补充，直接发给我就行。
> **EN:** **Gathering evidence — please don't refresh, restart, update, or close anything.** If you have more detail about the bug to add meanwhile, just send it over.

That line replaces any "when did it happen / what were you doing" interrogation.
This applies to **any software or game**, not only AI tools — as long as the user's
environment is reachable and they grant the permission.

### 5. Capture evidence (L0 → L3)
Follow `references/evidence.md`. Read-only commands only: no writes, no restarts, no config edits.
Anything you could not reach gets marked `not captured` in the report — never filled in from memory.

### 6. Deduplicate
```bash
gh issue list --repo <owner/repo> --state all --search "<keywords>"
```
A hit → ask the user whether to add a comment to the existing issue instead of filing a new one.

### 7. Check the target repository's issue templates
```bash
gh api repos/<owner/repo>/contents/.github/ISSUE_TEMPLATE --jq '.[].name'
```
- **Template fits** → start from it: `gh issue create --template "<name>"`, and use *its* section headings.
  Using `gh` also skips web-only required fields (forms that force a log upload).
- **Template demands uploading logs/debug output** → **ask the user first**:

> **ZH:** 这个仓库的模板要求附日志。**要我把日志传上去吗？**
> · 传：日志和配置会上传到**公开**的粘贴服务，凭链接的人都能看到。
> · 不传也行，我照常提 issue，正文里标 `logs not attached`，维护者需要时会再找你。
> 你决定。
>
> **EN:** This repo's template asks for logs. **Should I attach them?**
> · If yes: your config and logs get uploaded to a **public** paste service — anyone with the link can read them.
> · If no: I'll file it anyway with `logs not attached`; maintainers can ask later.
> Your call.

Scan the logs for secrets **before** offering to upload. If the user declines, proceed without them.

### 8. Privacy check — reminder, not a veto
Run `scripts/privacy_scan.py <draft-file>`. Two levels (see `references/privacy.md`):

| Level | Examples | What you do |
|---|---|---|
| **1 — identity / location / history** | username, local paths, chat logs, ids | Warn **once**, continue on yes |
| **2 — secrets** | password, API key, token, private key | **Second confirmation**: state the consequence, then wait for an explicit reply |

Content the user pasted themselves gets the same warnings.
**You never upload logs or capture anything on your own initiative.** If the user insists after
being warned, file it as they say.

### 9. Draft the report
Six sections, in the target repo's language — see `references/report.md` and `templates/bug-report.md`:
`Description / Steps to Reproduce / Expected / Actual / Environment / Related`.
When the repo supplies a template, its headings win and these six are only the fallback.

### 10. User approval — hard gate
Show the **full Title and Body**. Nothing is sent until the user explicitly says yes.
Never treat silence, "ok", or an earlier instruction as permission for *this* issue.

### 11. File it, attach images, read it back
```bash
gh issue create --repo <owner/repo> --title "<title>" --body-file draft.md \
  [--template "<name>"] [--attach './screenshot.png#what it shows']
```
Then verify — a successful command is not a successful report:
```bash
gh issue view <number> --json body,title,url,state
```
Re-run the privacy scan on what actually landed, then hand over the URL.
Images are supported by `--attach` (up to 50 files); in a follow-up comment use
`gh issue comment <n> --attach './img.png#alt'`.

**Labels will be empty** — external contributors have no permission to add them and some
templates reference labels that do not exist. That is normal, not a failure.

### 12. (Optional) Watch for replies
```bash
gh issue view <number> --comments
```

---

## Fallbacks — always end with something usable

| Situation | What to do |
|---|---|
| `gh` not logged in | Offer `gh auth login`, or hand over the whole body as one block for manual paste |
| No network | Deliver the body as one block |
| Target is not a GitHub repo (Discord, forum, support desk) | Deliver the body as one block — they post it themselves |
| Private repo / no access | Say so plainly, then deliver the body |
| Evidence unreachable (permissions, restart already done) | File with `not captured` noted — never fabricate |

"Deliver as one block" means: Title on its own line, then the entire body inside a single code
block, so the user can select and copy it in one action.

---

## Never

- Never run a log-upload command (e.g. `hermes debug share`) on the user's behalf — that option
  belongs to Step 7, and only after the user says yes.
- Never claim evidence you did not actually read.
- Never file without Step 10.
- Never put your own local paths, usernames, or this repository's internals into a report.
