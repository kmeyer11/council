# presentations

Makes PowerPoint decks from a saved style. Each deck gets its own copy of the style, so slides added later still match. See `CONTEXT.md` for how it fits together.

## Use

```bash
.venv/bin/python -m presentations.cli styles                                   # list styles
.venv/bin/python -m presentations.cli sample clean                             # every layout in a style
.venv/bin/python -m presentations.cli new --style clean --slug kvartal --title "Kvartalsmøde"
.venv/bin/python -m presentations.cli render decks/2026-10-19-kvartal          # .pptx + preview PNGs
```

Previews are made with Keynote. Layouts and their fields: `presentations/sample.yaml`.
