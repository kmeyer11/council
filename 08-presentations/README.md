# presentations

Makes PowerPoint decks. Each deck starts from a copy of the base style `bold`, tailored to that talk, so slides added later still match. See `CONTEXT.md` for how it fits together.

## Use

```bash
.venv/bin/python -m presentations.cli styles                                   # list styles
.venv/bin/python -m presentations.cli sample bold                              # every layout in the base style
.venv/bin/python -m presentations.cli new --style bold --slug kvartal --title "Kvartalsmøde"
.venv/bin/python -m presentations.cli render decks/2026-10-19-kvartal          # ~/Desktop/kvartal.pptx + preview PNGs
```

Previews are made with Keynote. Layouts and their fields: `presentations/sample.yaml`.
