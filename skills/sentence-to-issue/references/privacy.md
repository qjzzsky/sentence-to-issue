# Privacy: redacted by default, verified by the scanner, exceptions on request

The design has three moves, in order: **redact by default → verify with the
scanner → ask only when the target repository actually requires it.**

## 1. Default: redact

Draft with the sensitive parts replaced by `<redacted>`, and leave a visible
"this was redacted" trace in the body — never silently delete context the
maintainer needs to reproduce the bug. Two kinds get redacted:

- **identity / location / history** (level 1): usernames, local file paths,
  e-mail addresses, chat / session ids, social profile links, internal hostnames
- **secrets** (level 2): passwords, API keys, tokens, session cookies, private
  keys, connection strings with credentials

Then **show the user the redaction list before anything else** — in the chat,
never in the draft:

| Position | What was removed | Why | Asked because the repo requires it? |
|---|---|---|---|

That list is for the user's eyes only. It never goes into the draft, into any
file that will be submitted, or into a gist.

## 2. Verify: the scanner is a gate, not an alarm

Run `scripts/privacy_scan.py <draft>`:

| Exit | Means | You do |
|---|---|---|
| 0 | redaction complete | continue |
| 1 or 2 | redaction incomplete | **redact what it found, then re-run** |

There is no "the user said it is fine, send it as-is" branch here. Exit 1 or 2
is the scanner saying the redaction pass missed something — fix the draft, not
the user's decision. Re-run until it is 0.

## 3. Exceptions: only when the repository asks

Ask **only** when the target repository's own issue template or CONTRIBUTING
guide **explicitly requires** that kind of content. Quote the requirement
verbatim, so the user can see why they are being asked at all:

> **ZH:** 这个仓库的模板明确要求附上…（原文：「…」）。要我把这一处恢复吗？
>
> **EN:** This repo's template explicitly asks for … (its words: "…"). Restore that one spot?

If they say yes, restore **only that spot** — an excerpt over the whole file —
and keep everything else redacted. Secrets stay stricter: even when the repo
demands them, redact the secret *inside* the excerpt first; drop that redaction
only when the user explicitly names that exact text.

## What each level decides now

Levels no longer decide *whether* to stop — the scanner does that. They decide
*how to ask* when an exception is on the table:

| Level | Kind | Exception policy |
|---|---|---|
| **1** | identity / location / history | may be offered **if the repo requires it**; the user decides |
| **2** | secrets | **never leaves by default**; stays redacted inside any excerpt unless the user names that exact value |

## Supplying a file the repo asks for

`gh issue create --attach` accepts **images and video only** — a log file cannot
ride along that way. When the repository asks for one and the user agrees, offer
in this order:

1. Paste the relevant excerpt into the body — you do it, and you scan the draft
   **before and after** pasting.
2. The whole file via `gh gist create <file>` — **ask public or secret every
   single time**, and say in the body which one it is.
3. The user uploads it on the web themselves.

To let the scanner accept a value the user authorised, pass it explicitly:
`privacy_scan.py <draft> --allow '<the exact value>'` (repeatable, or
`--allow-file <file>` with one value per line). Everything else in the draft is
still checked, and every other secret still blocks. `--skip-scan` turns the
scanner off for the **whole** draft — last resort, never a default.

## What you never do on your own

- Never upload anything **without authorisation**. Once the user has authorised
  it, the CLI can carry it out: paste an excerpt into the body, or
  `gh gist create` the file. Always state in the body what was uploaded and how
  visible it is.
- Never broaden the capture beyond what the report needs.
- Never paste this repository's own internal notes, paths, or your session
  history into a report.
- Never write the redaction list into anything that gets submitted.

## The word list lives in the scanner

`scripts/privacy_scan.py` holds the detection patterns (placeholders, not real
names). Run it on the draft, run it again on what actually landed after filing,
and act on its exit codes using the gate table above.

## What the `privacy-allow` marker can and cannot do

An inline `<!-- privacy-allow --> ... <!-- /privacy-allow -->` block excuses
**level-1 findings only** — that is what the author block of a public README
uses, content that is published on purpose. A password, token or private key
inside such a block is still reported and still blocks: the marker is written by
whoever drafts the report, and untrusted input (logs, web pages, third-party
repositories) may carry it on purpose.

For values the user authorised **in this conversation**, `--allow` is the
mechanism — explicit, per-value, and visible in the scan output. The marker is
not.

## The scanner may miss, and redaction is not anonymity

Two boundaries to state plainly, because both are limits on what redaction buys you:

1. **The scanner is heuristic.** It rebuilds two extra views of the text (HTML comments
   removed, newlines joined) because that is what a reader sees when GitHub renders the
   issue — but a value that is split, spaced out or encoded in some other way can still
   slip through, and the `~N [view]` line numbers on rebuilt hits are approximate.
2. **Redaction lowers exposure; it is not anonymity.** The issue is filed under the
   user's GitHub account, and what is left can still identify them.

**Before the user answers in Step 10, say both out loud:** this report is redacted,
**not anonymous** — it will be filed under their GitHub account and the remaining details
can still point at them; and the scanner is a gate, not a guarantee.

**The last line of defence is Step 10: the user reads the full title, the full
body and the redaction-list summary before anything is filed.** The scanner is a
gate, never a substitute for that.
