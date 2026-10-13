# Sentence to Issue · 一句话提 GitHub issue

The full workflow lives in **[skills/sentence-to-issue/SKILL.md](./skills/sentence-to-issue/SKILL.md)** — read it and follow it.

Trigger: the user says one sentence about something broken and wants it filed as a GitHub issue —
"file an issue", "report this bug to the repo", "one sentence issue", or in Chinese
"一句话提 GitHub issue" / "帮我把这个 bug 传上去".

Two things you must honour:

1. **Reply in the language the user writes in.** The issue body follows the target repository's language.
2. **Never send without Step 10** — show the full Title and Body and wait for an explicit yes.

Privacy is redact-by-default: personal details and secrets are replaced with <redacted> and
the removal list is shown to the user; the scanner is a gate (non-zero exit means redact and
re-run), and nothing is uploaded without the user's explicit authorisation.
