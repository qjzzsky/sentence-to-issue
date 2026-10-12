# Pitfalls that cost us real reports

## Web forms with a required log upload
Some repos force `Debug Report`-style fields in the browser. The `gh` CLI does not go through
the web form, so those requirements do not apply when you file from the command line — but
**never treat that as permission to upload logs**. Ask the user (Step 7), accept "no", and note
`logs not attached` in the body. Note that `--attach` accepts **images and video only** —
a log file cannot ride along that way; the excerpt has to go into the body text.

## Labels come back empty
**This flow never passes `--label`**, so a fresh issue shows an empty `labels` array —
that is normal, not a failure. Do not add labels yourself: external contributors have no
triage permission, and some templates reference labels the repo does not even have.
The repo's sweeper bot usually labels within minutes.

## Images
`gh issue create --attach './file.png#alt text'` uploads images and videos (up to 50 per
command). For a later comment: `gh issue comment <n> --attach './file.png#alt'`.

**The `--attach` path must match the body reference character for character** — body says
`![alt](./file.png)`, so pass `./file.png#alt`. A mismatch (absolute path vs `./name`, or a
different directory) makes gh *append* a second copy of the image instead of rewriting the
reference, leaving a dead `./file.png` link in the published body.
Deduping first: a screenshot the user pasted may already be enough evidence without re-uploading.

## Deduplication first
`gh issue list --repo <r> --state all --search "<keywords>"` before filing. If a match exists,
offer to comment on it instead. Repos with fast maintainers merge duplicates away within
minutes — a second identical issue is noise.

## git-bash hands POSIX paths to Python
Inside git-bash/MSYS, `pwd` and `mktemp` yield `/e/...` and `/tmp/...`. A native Windows
Python reads those as `C:\e\...` and `C:\tmp\...` — the file "does not exist". The script
normalises with its `native()` helper; keep using it for any path that crosses into Python.

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
