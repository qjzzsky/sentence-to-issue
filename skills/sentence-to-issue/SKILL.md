---
name: sentence-to-issue
description: >-
  Use when the user says "file an issue", "report this bug to the repo",
  "one sentence issue", or the Chinese equivalents "一句话提 GitHub issue" /
  "帮我把这个 bug 传上去" - turn one sentence of description into a filed GitHub
  issue on any public repository. Gathers evidence, privacy-checks the draft,
  writes the report, submits with the gh CLI, then reads it back to verify.
  Works for any software or game, not only AI tools.
license: MIT
---

# Sentence to Issue · 一句话提 GitHub issue

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

### 2. Resolve the target repository — three sources
1. `git remote get-url origin` in the current working directory
2. The user's own words: an `owner/repo`, or a full `https://github.com/...` link
3. **Explicit repository URLs in the project's own config** — `package.json`'s `repository`
   field, `pyproject.toml`'s `repository` / `homepage`. These name a repository outright.
   A `LICENSE` copyright line names at most an **owner**, never a repository: it may
   *confirm* a repo you already locked onto, it must never *choose* one
   (`Never guess the repository`, Step 1).

There is **no keyword search** — if none of the three yields a repository, ask the user for it.
Anything resolved from source 3 is confirmed with the user before it is used to file.

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
- **Template fits** → fetch it and fold its headings into your draft:
  ```bash
  gh api repos/<owner/repo>/contents/.github/ISSUE_TEMPLATE/<file> --jq .content | base64 -d
  ```
  Fill those headings from your evidence, then file with `--body-file` **only**.
  ⚠️ `gh issue create` **rejects** `--template` combined with `--body`/`--body-file`
  (`--template is not supported when using --body or --body-file`) — merge first, then file.
  Filing through `gh` also skips web-only required fields (forms that force a log upload).
- **Template listing quirks** (all seen in the wild):
  - `config.yml` appears in the listing but is **not a template** (`blank_issues_enabled` +
    `contact_links`) — skip it.
  - `.yml` issue **forms** are not markdown: field labels live in `body[].attributes.label`.
    There is no heading to fold — read them as a field list instead.
  - `.md` templates carry YAML frontmatter (`--- name/about/title/labels/assignees ---`).
    Strip it first, or you will send `labels: ''` and friends verbatim.
- **The template or CONTRIBUTING explicitly requires content you redacted** → **ask the
  user first**, quoting the requirement verbatim (full rules in `references/privacy.md`):

> **ZH:** 这个仓库的模板明确要求附上…（原文：「…」）。要我把这一处恢复吗？
> · **推荐**：只把相关片段**贴进正文** —— 贴之前、贴之后我都会再扫一遍敏感信息；
> · 整份文件也可以由我用 `gh gist create` 代传 —— **每次都要你先选 public 还是 secret**，
>   并且我会在正文里写明它是「公开链接」还是「仅链接可见」；
> · 或者你自己在网页上传。
> 不给也行，我照常提 issue，正文里标 `not attached`，维护者需要时会再找你。
> 你决定。
>
> **EN:** This repo's template explicitly asks for … (its words: "…"). **Restore that one spot?**
> · **Preferred:** paste the relevant excerpt into the body — I re-scan before **and** after.
> · The whole file can go up via `gh gist create` — **you pick public or secret every time**,
>   and the body will state which one it is.
> · Or upload it on the web yourself.
> · Or skip it: I'll file with `not attached` and maintainers can ask later.
> Your call.

`--attach` takes **images and video only** — a log file cannot ride along that way.
Scan any excerpt **before and after** it goes in. Restore only the spot the repository
asked for; everything else stays redacted.

### 8. Privacy: redact by default, verify with the scanner, show the list

Three moves, in order (full rules in `references/privacy.md`):

1. **Redact by default.** Replace identity/history details and secrets with `<redacted>`
   and leave a visible "redacted" trace. Then show the user the **redaction list** in
   chat — position / what was removed / why — and keep that list out of every file that
   will be submitted.
2. **Verify with the scanner** (again after pasting any excerpt).
   `scripts/privacy_scan.py <draft>` → exit 0 continues; exit 1 or 2 means the redaction
   pass missed something, so **redact it and re-run**. That exit code is not a prompt to
   ask the user whether to send as-is.
3. **Exception only when the repo requires it** — quote the requirement, restore only
   that spot; secrets stay redacted inside any excerpt unless the user names that exact
   value. Authorised values are passed explicitly: `--allow '<value>'` (repeatable, or
   `--allow-file <file>`). `--skip-scan` turns the scanner off for the whole draft —
   last resort.

| Level | Kind | What it decides |
|---|---|---|
| **1 — identity / location / history** | username, local paths, chat logs, ids | redacted by default; may be offered **if the repo requires it** |
| **2 — secrets** | password, API key, token, private key | redacted always; leaves only when the user names that exact value |

**You never upload or capture anything without authorisation.** Once the user has
authorised it in Step 7, the CLI can carry it out (`gh gist create`, or an excerpt
pasted into the body).

### 9. Draft the report
Six sections, in the target repo's language — see `references/report.md` and `templates/bug-report.md`:
`Description / Steps to Reproduce / Expected / Actual / Environment / Related`.
When the repo supplies a template, its headings win and these six are only the fallback.

### 10. User approval — hard gate
Show the **full Title and Body**, plus a short summary of the **redaction list** — what
was removed and stayed out — so the user can see what the issue will NOT contain.
Nothing is sent until the user explicitly says yes.
Never treat silence, "ok", or an earlier instruction as permission for *this* issue.

### 11. File it, attach images, read it back

Preferred — one script runs dedupe → scan → file → read back → re-scan, in that order.
Path is relative to this SKILL.md (the `scripts/` folder next to it):
```bash
scripts/file_issue.sh \
  --repo <owner/repo> --title "<title>" --body-file draft.md \
  [--attach './screenshot.png#what it shows']
```
**Call it only after Step 10** — the script has no approval gate of its own.

Or by hand:
```bash
gh issue create --repo <owner/repo> --title "<title>" --body-file draft.md \
  [--attach './screenshot.png#what it shows']
```
⚠️ Never put `--template` beside `--body-file`: gh rejects the combination outright.
Merge the template into the draft first (Step 7).

Then verify — a successful command is not a successful report:
```bash
gh issue view <number> --json body,title,url,state
```
Re-run the privacy scan on what actually landed, then hand over the URL.
Images ride along with `--attach` (up to 50 files); a follow-up comment takes them too:
`gh issue comment <n> --attach './img.png#alt'`.

**This flow never passes `--label`**, so a fresh issue shows an empty `labels` array — that
is normal. Do not add labels yourself: external contributors have no permission, and the
repo's sweeper labels it within minutes.

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

- Never upload anything **without authorisation**. Once the user has authorised it in
  Step 7, the CLI **can** carry it out: paste an excerpt into the body, or
  `gh gist create` the file — `--attach` itself only accepts images and video.
  Always state in the body what was uploaded and how visible it is.
- Never claim evidence you did not actually read.
- Never file without Step 10.
- Never put your own local paths, usernames, or this repository's internals into a report.
