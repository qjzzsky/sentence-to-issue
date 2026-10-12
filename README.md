# One-Sentence Issue

> **File an issue in one sentence.**
> 一句话提 GitHub issue — one sentence in, a filed GitHub issue out.

Tell your AI assistant what broke, in one sentence. It freezes the scene, gathers whatever
evidence your machine can reach, checks the draft for anything you would not want public,
writes the report, files it with the `gh` CLI, then **reads it back** to prove it landed.

Works for **any software, any game, any web app** — not only AI tools — as long as your
environment allows the capture and you grant the permission.

---

## 30 seconds

Install:

```bash
gh skill install qjzzsky/one-sentence-issue --agent claude-code
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

Nothing leaves your machine until you have seen the entire body and said yes.

---

## Install

**Path A — `gh skill` (48 agents: Claude Code, Cursor, Codex, Copilot, Gemini CLI, …)**

```bash
gh skill install qjzzsky/one-sentence-issue                 # interactive
gh skill install qjzzsky/one-sentence-issue --agent cursor  # specific agent
```

**Path B — any skill-based assistant (Hermes, custom setups)**

```bash
git clone https://github.com/qjzzsky/one-sentence-issue.git \
  ~/.hermes/skills/one-sentence-issue
```

**Requirements:** the `gh` CLI ([cli.github.com](https://cli.github.com)) and `gh auth login`.
Without them the workflow still works — it degrades to handing you the finished body to paste.

---

## The 12 steps

| # | Step | Detail |
|---|---|---|
| 1 | Parse your one sentence | what broke, which repo, what evidence you have |
| 2 | Resolve the repository | **two sources only**: local `git remote`, or the link/repo you gave |
| 3 | Capability probe | decides how deep it can capture — chat only ⇒ L0 |
| 4 | Freeze the scene | "don't refresh, restart, update or close anything" |
| 5 | Capture L0→L3 | **read-only**, uncaptured evidence marked `not captured` |
| 6 | Deduplicate | existing issue ⇒ offer to comment instead |
| 7 | Repo's own issue template | fits ⇒ use it; **asks for logs ⇒ asks you first** |
| 8 | Privacy check | level 1 warns once · **level 2 (keys/tokens) needs a second confirmation** |
| 9 | Draft the report | six sections, in the repo's language |
| 10 | **You approve** | the full Title + Body, before anything is sent |
| 11 | File, attach, read back | `gh issue create --attach …` then `gh issue view …` re-scan |
| 12 | (optional) Watch replies | `gh issue view <n> --comments` |

---

## Language

| Layer | Language |
|---|---|
| Chat with you | whatever language you write in |
| The issue body | the target repository's language (English by default) |
| `SKILL.md` + `references/` | English — they are read by the assistant, not by you |

---

## Privacy: warn, then your call

**The default is: capture nothing sensitive, upload nothing on your own initiative.**

| Level | Examples | Behaviour |
|---|---|---|
| 1 — identity / location / history | username, local paths, chat history | warn **once**, you decide |
| 2 — secrets | password, API key, token, private key | **second confirmation**: the consequence first, then you decide |

Content you pasted yourself gets the same warnings. If you insist after the warning, it files
as you say.

It never runs a log-upload command for you. When a repository template demands logs, it asks
you — including "you can skip this, the issue still goes through".

---

## Boundaries

- **GitHub only.** Targets outside GitHub (Discord, forums, support desks) ⇒ you get the whole
  body as one block to paste yourself. That is a success, not a failure.
- **Read-only forensics.** No writes, no restarts, no config edits — those destroy the state
  being recorded.
- **Nothing without your yes.** Step 10 is a hard gate.
- **Labels will be empty.** External contributors cannot add them and some templates reference
  labels that do not exist. The repo's bot usually labels within minutes.

---

## Real examples

Reports filed with this exact method (read-only evidence, privacy scan, `gh` submission,
read-back verification):

- [Desktop batch clarify — recommended option reads as pre-selected](https://github.com/NousResearch/hermes-agent/issues/137132)
- [Viewport jumps to the upper half mid-chat](https://github.com/NousResearch/hermes-agent/issues/136914)
- [Completed turns vanish after switching sessions](https://github.com/NousResearch/hermes-agent/issues/134290)
- [`.restart_pending.json` never self-clears](https://github.com/NousResearch/hermes-agent/issues/127316)

---

## How it differs from what already exists

| Existing | What it does | What this adds |
|---|---|---|
| issue skills bound to one project | file issues for that project | **any repository**, resolved from `git remote` or your link |
| "deep dive then save locally" | writes a file, never files | actually files, then reads back |
| single-repo bug report skill | sanitized draft, one project | **L0→L3 layered capture**, an executable privacy scanner, template awareness |

---

## Layout

```
one-sentence-issue/
├── README.md / README.zh-CN.md
├── LICENSE · .gitignore
├── AGENTS.md, CLAUDE.md          one-line pointers to SKILL.md
└── skills/
    └── one-sentence-issue/
        ├── SKILL.md              the workflow (read by the assistant)
        ├── references/           evidence layers · privacy rules · report shape · pitfalls
        ├── templates/            bug report and feature request bodies
        └── scripts/
            ├── privacy_scan.py   two-level scanner, generic patterns only
            └── file_issue.sh     dedupe → scan → file → read back → re-scan
```

Everything the assistant needs lives **inside `skills/one-sentence-issue/`** — that is the
directory `gh skill install` copies, so a skill installed without it would be missing its
scanner and templates.

---

## License

[MIT](./LICENSE) © 2026 qjzzsky.

Brief excerpts from other open-source projects keep their origin and license noted in
`skills/one-sentence-issue/references/pitfalls.md`.
