# Evidence: what to capture, and how deep you can go

The workflow captures evidence for **any software, any game, any web app** — not only AI tools.
Two things decide the depth: what your environment can reach, and what permission the user gives.

## Capability probe (do this before promising anything)

Inventory what you actually have in this session:

| You have | You can reach |
|---|---|
| Terminal / shell | L2 — read-only commands: logs, processes, environment, `git log` |
| File read | L1 — files the user names, logs on disk, config in front of you |
| Screenshot / vision | L1 — a picture the user pastes, a crash dialog |
| Browser tools | L1 — console output, network tab, page state |
| Installed skills / plugins | L3 — anything purpose-built they already installed |
| Chat only | L0 — the user's words and what they paste |

Write down the deepest layer you can reach. **Do not promise a capture you have no tool for.**
If the user's environment or permission does not allow it, stop at the layer you have — never
escalate on your own.

## The four layers

The level says **how deep the capture can go**, not what kind of tool it is: the same browser
can be L1 (read the console) or L3 (a dedicated capture skill you installed). Pick the level
from the result, not the category.

### L0 — what the user gives you (always available)
Their description, pasted error text, screenshots, screen recordings.
Ask for it only if it is missing and it matters; the user may also volunteer extra detail
while you are working — take it as it arrives.

### L1 — what is right in front of you
Files open in this session, the current project, `git log`, the page on screen.
Read, never modify.

### L2 — read-only commands
Log files, process lists, environment variables, event viewers, crash dumps, game logs.

**Read-only is a hard rule**: no writes, no restarts, no config edits, no installs, no cleanup.
Restarts and refreshes destroy the very state you are trying to record.

### L3 — purpose-built tools already installed
Whatever the user has: a bug-capture skill, a browser collector, an error notebook, a log reader.
If none exists, move on — this layer is optional and never required.

## Rules

- **Mark what you could not get** as `not captured` in the report. Silence is not an excuse,
  and guessing is worse than an empty field.
- **Permission is the user's to give.** Ask once, accept no for an answer, and record that
  the permission was declined if it changes what you can report.
- **A destroyed scene is still a scene.** If the user already restarted/refreshed before you
  got there, say so in the report (`restarted before capture`) instead of hiding it.
- **No fabrication.** Every line in the report must come from something you actually read.
