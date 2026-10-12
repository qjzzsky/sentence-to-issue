# Pitfalls that cost us real reports

## Web forms with a required log upload
Some repos force `Debug Report`-style fields in the browser. The `gh` CLI does not go through
the web form, so those requirements do not apply when you file from the command line — but
**never treat that as permission to upload logs**. Ask the user (Step 7), accept "no", and note
`logs not attached` in the body.

## Labels come back empty
External contributors cannot add labels, and some templates reference labels that do not exist
in the repo. `--label` fails silently — the `labels` array in the response stays empty.
**Empty labels are normal.** Do not retry, do not report it as an error; the repo's sweeper
bot usually labels within minutes.

## Images
`gh issue create --attach './file.png#alt text'` uploads images and videos (up to 50 per
command). If the body already contains `![alt](./file.png)`, that reference is rewritten to the
uploaded URL. For a later comment: `gh issue comment <n> --attach './file.png#alt'`.
Deduping first: a screenshot the user pasted may already be enough evidence without re-uploading.

## Deduplication first
`gh issue list --repo <r> --state all --search "<keywords>"` before filing. If a match exists,
offer to comment on it instead. Repos with fast maintainers merge duplicates away within
minutes — a second identical issue is noise.

## `gh` is not logged in
`gh auth login` opens a browser flow. If the user cannot or will not, fall back to delivering
the whole body as one block so they can paste it into the web form themselves.

## The target is not a GitHub repo
Games, closed-source apps, Discord servers and forums have no `gh` path. Deliver the body as
one block — that is a successful outcome, not a failure.

## Read the body back
A successful command is not a successful report. Always run
`gh issue view <n> --json body,title,url`, re-run the privacy scan on what actually landed, and
only then hand over the link.

## Attribution
Brief code excerpts from other open-source projects (file paths, short snippets) must carry
their origin and license. This project is MIT.
