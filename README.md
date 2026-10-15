# Sentence to Issue

[中文简体](./README.zh-CN.md)

> **Report a bug to any GitHub project — in the shape maintainers ask for: read-only
> evidence, no invented diagnosis, and nothing filed until you approve it.**
>
> A bug report that guesses at a root cause is worse than no report at all.

**As long as the program is open source and hosted on GitHub, anything can be reported
through this skill — software, games, web apps, AI-agent skills alike.** It runs in
Claude Code, Cursor, Codex and 75+ other agents.

When a bug shows up, tell your AI assistant what broke — it starts investigating.
**Don't refresh, restart, update, or close anything meanwhile. If you have more detail,
send it over.**

While investigating it gathers evidence where your permissions allow, **redacts** the
sensitive details **it finds** in the draft, **lists what it removed, item by item**, and only
asks you to supply those details when the repository's own template requires them. Then it
finds the matching GitHub repository and files the issue with `gh`.

When that is done it checks everything once more, confirms the issue went through, and hands
you the link.

---

## Quick start (30 seconds)

Install:

```bash
npx skills add qjzzsky/sentence-to-issue      # skills.sh — picks your agent automatically
gh skill install qjzzsky/sentence-to-issue --agent claude-code
```

Then, in any assistant that has it loaded:

> The submit button spins forever on this page — console throws `undefined`. File it for me.

What happens next:

```
Gathering evidence — please don't refresh, restart, update, or close anything.
        ↓  capture (read-only)        ↓  privacy check
        ↓  dedupe + repo template     ↓  draft
        ↓  YOU approve the full body  ↓  file + attach screenshots + read back
https://github.com/<owner>/<repo>/issues/123
```

Nothing is filed until you have seen the entire body and said yes.

---

## Install

**Path A — `gh skill` (48 agents: Claude Code, Cursor, Codex, Copilot, Gemini CLI, …)**

```bash
gh skill install qjzzsky/sentence-to-issue                 # interactive
gh skill install qjzzsky/sentence-to-issue --agent cursor  # non-interactive, one agent
gh skill install qjzzsky/sentence-to-issue sentence-to-issue --agent claude-code
#  ^ plain form for scripts: repository, then skill name
```

**Path B — Hermes**

```bash
hermes skills install qjzzsky/sentence-to-issue
```

**Path C — `npx skills`** (skills.sh, 79 agents)

```bash
npx skills add qjzzsky/sentence-to-issue
```

`hermes skills install` also takes a direct `SKILL.md` URL. If you would rather clone by
hand, put it in the directory `hermes skills list` reports for your platform — the skills
folder is **not** the same path on Windows and Unix:

```bash
git clone https://github.com/qjzzsky/sentence-to-issue.git <your-skills-dir>/sentence-to-issue
```

**Requirements:** the `gh` CLI ([cli.github.com](https://cli.github.com)) and `gh auth login`.
Without them the workflow still works — it degrades to handing you the finished body to paste.

---

## The issue submission steps

| # | What the AI does | How the AI does it |
|---|---|---|
| 1 | Reads your sentence | Works out from your description what broke, which GitHub repository it belongs to, and what evidence there is |
| 2 | Finds the right repo | Three sources to check: the project's own git remote, the link you gave, or an explicit repository URL in the project's own config (`package.json` / `pyproject.toml`). A LICENSE copyright line only confirms an owner — it never picks the repo |
| 3 | Checks available tools | Checks the permissions and skills it can draw on — file access and a shell mean more evidence, a chat window alone means less |
| 4 | Before it digs in | It warns you: "Don't refresh, restart, update, or close anything. Anything else you remember about the bug, send it over." |
| 5 | Investigates | The bug only, recorded as found, no files touched |
| 6 | Checks for duplicates | If a similar issue already exists → it suggests adding detail in the comments instead of opening a new one |
| 7 | Checks the issue template | Uses the repository's own template when there is one; if the template wants logs, it asks you first |
| 8 | Redacts by default | Replaces personal details and secrets with `<redacted>`, shows you the list of what was removed, then runs the scanner — a non-zero exit means redaction is incomplete, so it redacts and re-runs. Nothing reaches the issue without your consent |
| 9 | Writes the issue | Body written to the target repository's requirements |
| 10 | Shows you the issue | The full title and body for review — it publishes only after you approve |
| 11 | Files and verifies | Files it, then checks it again once it is visible on GitHub |
| 12 | Follows up (optional) | You can ask the AI to track the issue's progress |

The commands behind those rows:

```bash
gh issue list --repo <owner/repo> --state all --search "<keywords>"        # step 6
gh api repos/<owner/repo>/contents/.github/ISSUE_TEMPLATE --jq '.[].name'  # step 7
scripts/privacy_scan.py draft.md                                           # step 8
gh issue create --repo <owner/repo> --title "<title>" --body-file draft.md \
  --attach './screenshot.png#what it shows'                                # step 11
gh issue view <number> --json body,title,url,state                         # verify
gh issue view <number> --comments                                          # step 12
```

Evidence depth runs L0 → L3 (chat only → files the user hands over → read-only commands →
live process state). Anything out of reach is recorded as `not captured`, never filled in
from memory — see `skills/sentence-to-issue/references/evidence.md`.

---

## Which language is used where

| Layer | Language |
|---|---|
| The assistant's replies to you | whatever language you write in |
| The issue body | the target repository's language (English by default) |
| `SKILL.md` + `references/` | English — they are read by the assistant, not by you |
| This README | English |

---

## Privacy: redacted by default

**The default is: redact what is sensitive, show you the list, upload nothing on its own
initiative.** Personal details and secrets are replaced with `<redacted>` in the draft, and
you are shown what was removed before anything is filed.

Redaction lowers exposure — **it is not anonymity**: the issue is filed under your GitHub
account, and what is left can still point at you. We are careful, not omniscient; see
**What this is not** below.

| Level | Examples | Behaviour |
|---|---|---|
| 1 — identity / location / history | username, local paths, chat history | redacted by default; offered back to you **only if the repo's template requires it** |
| 2 — secrets | password, API key, token, private key | always redacted in the draft; included only when you name that exact value |

The scanner is a **gate**, not a reminder: a non-zero exit means the redaction pass missed
something, so it redacts and re-runs rather than asking you to send as-is. When the
repository does ask for content it redacted, it offers — in order — pasting an excerpt into
the body (re-scanned before and after), `gh gist create` for a whole file (**you pick public
or secret every time**), or you uploading it yourself. `gh issue create --attach` takes only
images and video, so a log file cannot ride along that way.

**What this is not:** the scanner is heuristic, not a guarantee. A value that is split across
lines, spaced out, or encoded in some other way can still slip past it — we are careful, not
omniscient. The last checkpoint **before anything is filed** is Step 10: you read the full
title and body. It is a checkpoint, not a proofreader — you are not expected to catch what
the scanner missed; the point is that nothing goes out before you have looked.

---

## What it does and doesn't do

- **GitHub only.** Targets outside GitHub (Discord, forums, support desks) ⇒ you get the whole
  body as one block to paste yourself. That is a success, not a failure.
- **Read-only forensics.** No writes, no restarts, no config edits — those destroy the state
  being recorded.
- **Nothing without your yes.** Step 10 is a hard gate.
- **Labels will be empty.** External contributors cannot add them and some templates reference
  labels that do not exist. The repo's bot usually labels within minutes.

---

## Real feedback from developers — successful cases

### 1. The AI assistant itself breaks — one sentence, from inside the conversation

**Scenario: the open-source AI assistant you use on GitHub breaks.** Install this skill, tell
the AI in one sentence what went wrong — it captures the evidence, scans it, summarizes, and
files the issue for you.

- **[#137132](https://github.com/NousResearch/hermes-agent/issues/137132)** — the recommended
  option in a batch clarify card carries a resting highlight, so it reads as pre-selected;
  the user skips it and the batch confirms with a question unanswered. *(feature request)*
- **[#136914](https://github.com/NousResearch/hermes-agent/issues/136914)** — reading a long
  transcript, the viewport jumped to the upper half by itself; three rows were missing the
  display index, sending the session down a different read path.
- **[#134290](https://github.com/NousResearch/hermes-agent/issues/134290)** — after switching
  sessions, completed turns vanished from the view even though every row was still in the
  database.
- **[#127316](https://github.com/NousResearch/hermes-agent/issues/127316)** — a failed channel
  left the restart marker stuck, so healthy channels silently stopped receiving their
  gateway-online notice.

### 2. A skill you installed breaks — file it in that skill's own repository

**Scenario: a skill pulled from GitHub misbehaves.** You already have the reproduction, and
that skill's repository is where its maintainer looks.

- **[#21](https://github.com/isjiamu/gzh-design-skill/issues/21)** — an installed
  WeChat-formatting skill trips the editor's content check: gradients are rejected in dark
  mode. Suggested defaulting to solid colours, or warning at check time. *(closed — addressed
  by the author)*

All five came out of this workflow: read-only evidence → privacy scan → `gh` submission →
read-back verification.

---

## How we compare with similar projects

Several projects already treat bug **triage** and conversational issue **filing** as a
first-class workflow. We name them instead of describing them in the abstract — here is
what each does, and what this skill adds on top.

| Project | What it does | What this adds |
|---|---|---|
| [AgentiveStack/skills · `qa`](https://github.com/AgentiveStack/skills) (72★) | describes bugs conversationally and files durable GitHub issues in the project's own language while exploring the codebase in the background | the **target repository is yours to choose** — from `git remote` or your link, not locked to the current repo — plus scene-freezing, L0→L3 read-only evidence layers, and an executable privacy scanner |
| [eric-tramel/moraine · `bug-report`](https://github.com/eric-tramel/moraine) (117★) | prepares a sanitized bug report and holds **the same consent boundary as this skill**: show the final title and body, file only after explicit approval | it serves Moraine itself (it is a Moraine plugin); this runs against **any repository**, and ships the two-level scanner as a script rather than a described convention |
| [redpanda-data/ui-harness · `triage`](https://github.com/redpanda-data/ui-harness) (34★) | investigates a bug with `gh` and Jira and files a ticket carrying a TDD fix plan | forensics are **read-only by contract** (no writes, no restarts), the target repo's own issue template is folded in, and the body is scanned again after it lands |
| [rbaumier/skills · `issue`](https://github.com/rbaumier/skills) (5★) · [sidwood/skills · `bug-report`](https://github.com/sidwood/skills) | minimal-scope issues for the current project / conversational GitHub bug filing | evidence depth layers (L0 chat → L3 live process state), dedupe before filing, read-back verification |
| [bowen31337/bug-report-agent-skills](https://github.com/bowen31337/bug-report-agent-skills) (4★) | GitHub Issues / Linear / Bugzilla with detective-style root-cause work | template folding and post-file re-scan, plus the "don't refresh, restart, update, or close anything" freeze |

### What we honestly share, and what is actually different

This is not a new idea. The field already has several projects in the same lane, and
**`eric-tramel/moraine` already has the same sanitize + explicit-user-approval gate**
this skill calls Step 10. Four things no single one of them covers:

1. **Any target repository.** The repo comes from `git remote` or from your link — not
   locked to the current project, not locked to one vendor.
2. **Scene freezing + L0 → L3 read-only layers.** "Don't refresh, restart, update, or
   close anything" while evidence is captured read-only; anything unreachable is marked
   `not captured` instead of guessed.
3. **An executable privacy scanner** (`scripts/privacy_scan.py`, two levels). Most
   similar skills describe sanitizing in prose — this one runs it.
4. **Dedupe → fold the target repo's own template → file → read the body back and
   scan it again.**

None of the above is ours alone, and none of it needs to be.

---

## File structure

```
sentence-to-issue/
├── README.md / README.zh-CN.md
├── LICENSE · .gitignore
├── AGENTS.md, CLAUDE.md          short pointers to SKILL.md
└── skills/
    └── sentence-to-issue/
        ├── SKILL.md              the workflow (read by the assistant)
        ├── references/           evidence layers · privacy rules · report shape · pitfalls
        ├── templates/            bug report and feature request bodies
        └── scripts/
            ├── privacy_scan.py   two-level scanner, generic patterns only
            ├── file_issue.sh     dedupe → scan → file → read back → re-scan
            └── selftest.py       7-assertion regression guard (run with no args)
```

Everything the assistant needs lives **inside `skills/sentence-to-issue/`** — that is the
directory `gh skill install` copies, so a skill installed without it would be missing its
scanner and templates.

---

## About the author

<!-- privacy-allow -->
**qjzzsky · 曲靖中中**

- GitHub: [qjzzsky](https://github.com/qjzzsky)
- Website: [qjzzsky.com](https://qjzzsky.com)
- Bilibili: [space.bilibili.com/1546459](https://space.bilibili.com/1546459)
- Weibo: [weibo.com/u/1074366780](https://weibo.com/u/1074366780)

Built with [Hermes Agent](https://github.com/NousResearch/hermes-agent) and Xiaomi
MiMo v2.6 Flash — authored, tested, and published with their help.
<!-- /privacy-allow -->

---

## License

[MIT](./LICENSE) © 2026 qjzzsky.

Brief excerpts from other open-source projects keep their origin and license noted in
`skills/sentence-to-issue/references/pitfalls.md`.
