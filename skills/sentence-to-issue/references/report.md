# The report: six sections, then get out of the way

Default shape, in the **target repository's language** (English unless the repo says otherwise):

```markdown
## Description
What broke, in one or two plain sentences. No jargon you cannot explain to the user.
If the cause is unknown, say so in one sentence (e.g. "Cause not determined — this report
contains observations only"). Never leave it implied.

## Steps to Reproduce
1. ...
2. ...
3. ...

## Expected
What should have happened.

## Actual
What actually happened — error text verbatim, in a code block if it is multi-line.

## Environment
OS, app/tool version, install method. Only what you verified, or what the user told you.
Anything not captured is written as `not captured`.

## Related
Related issues, links, screenshots (`![alt](./file.png)` with `--attach`).
```

## When the repository has its own template

Its headings win; these six are only the fallback. Get the list with:

```bash
gh api repos/<owner/repo>/contents/.github/ISSUE_TEMPLATE --jq '.[].name'
```

then fetch it and fold its headings into your draft:
`gh api repos/<r>/contents/.github/ISSUE_TEMPLATE/<file> --jq .content | base64 -d`.
File with `--body-file` only — **gh rejects `--template` next to `--body-file`**
(`--template is not supported when using --body or --body-file`). Using `gh` also skips
web-only required fields (forms that only exist in the browser).

Some templates ask for a debug/log upload. That is Step 7 of the flow: ask the user, explain
the risk, and accept "no" as a complete answer.

## Style

- Plain sentences. If the user does not know a term, neither does the reader by default.
- Quote errors exactly — do not tidy up an error message.
- Keep it as short as it can be while still reproducible.
- The title is a symptom, not a verdict: "viewport jumps to the upper half mid-chat", not "rendering is broken".
- **No diagnosis.** Do not add a root-cause section, a hypothesis, or a suggested fix. If the
  repository's own template asks for one, say plainly that you are reporting observations only.
