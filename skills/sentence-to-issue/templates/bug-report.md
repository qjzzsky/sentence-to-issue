# Bug report — drop-in body

Fill the sections in the **target repository's language**. Delete any section you cannot
answer, and write `not captured` rather than guessing.

```markdown
## Description

What broke, in one or two plain sentences.

## Steps to Reproduce

1.
2.
3.

## Expected

What should have happened instead.

## Actual

What actually happened. Multi-line error output goes in a code block, quoted verbatim:

```
<paste the error here>
```

## Environment

- OS:
- App / tool version:
- Install method:
- Evidence not captured:

## Related

- Screenshots: `![alt](./screenshot.png)` — upload with `--attach './screenshot.png#alt'`
- Related issues:
```

If the repository supplies its own template, fold its headings into this body and file with
`--body-file` only — `gh issue create` refuses `--template` when `--body-file` is present.
