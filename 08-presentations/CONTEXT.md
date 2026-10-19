# presentations

Makes PowerPoint decks (.pptx) in a saved style. A **style** is a reusable look: colours, fonts, sizes, motif, and rules for writing slides. A **deck** is one presentation. It gets its own frozen copy of the style, so slides added months later still match, even if the style has changed since.

## Inputs

- `styles/{name}/style.md`: one reusable style. YAML front matter is what the renderer reads (colours, fonts, sizes, `motif`, `footer`, `logo`). The Markdown body is what you read before writing slides: mood, when to use it, rules. A logo or other file the style uses sits next to it.
- `decks/{date}-{slug}/`: one deck (gitignored output).
  - `style.md`: a copy of the style, made by `new`. It is the only style file this deck reads. Its `## This deck` section records purpose, audience, language, theme and every choice made while building. **Read it before adding slides.**
  - `deck.yaml`: the slides. The single source of truth for the content.
  - `images/`: photos used by this deck.
  - `{slug}.pptx`, `preview/slide-NN.png`: built by `render`. Don't edit them.
- `presentations/sample.yaml`: every layout once, with every field it takes. Copy blocks from here when writing a `deck.yaml`.
- Reference (every task): `../00-shared/conventions.md`

Brand colours already defined elsewhere (e.g. Røverne in `../03-website-making/assets/brand.md`) can be copied into a new style. Don't link to them: a style must stand alone.

Do NOT load images or the .pptx as text. Look at `preview/*.png` to see a deck.

## Process

All commands run from this folder with `.venv/bin/python -m presentations.cli …`. Setup once: `uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt` (Conductor's setup script does this). Talk to the user in their language (usually Danish).

### Defining a style ("lav en stil")

1. Ask, in one message: what it's for (work, school, a club, a pitch), the mood (calm, bold, playful), colours or a brand to take them from, a logo, and fonts if they care.
2. Copy `styles/clean/` to `styles/{name}/` and change the front matter and body. Keep fonts that ship with both macOS and Windows (Arial, Georgia, Verdana, Trebuchet MS, Times New Roman) unless the user names others. A .pptx shows its fonts only if the computer it's shown on has them.
3. `sample {name}` renders every layout to `decks/_samples/{name}/`. Look at every PNG in `preview/`, fix what's off, and show the user.
4. The user approves the style. Don't build decks on a style they haven't seen.

### Making a deck ("lav en powerpoint/præsentation")

1. `styles` lists the styles. Ask which one, unless it's obvious. Ask about purpose, audience, length (minutes) and language, and for the content: notes, a document, or keywords.
2. `new --style {name} --slug {short-name} --title "…"` creates the folder.
3. Fill in `## This deck` in the deck's `style.md` first, then write `deck.yaml`. Roughly 1 slide per 1.5–2 minutes. Follow the style's rules. Vary layouts. Put what the speaker says in `notes`, not on the slide.
4. Every fact (numbers, names, dates) must come from the user's material. If one is missing, ask.
5. `render decks/{folder}`. Fix every `WARNING` (text that probably overflows), then look at every PNG in `preview/`. Fix and render again.
6. Show the user the previews and the path to the .pptx, plus a list of what you wrote yourself, so they can change it.

### Adding slides to a deck later

1. Read the deck's `style.md` (front matter and `## This deck`) and the whole `deck.yaml`.
2. Add the slides to `deck.yaml` in the same voice and with the same layouts. Use only what the deck's `style.md` allows.
3. If you made a new choice (a new layout, a new kind of image), add it under `Decisions` in `## This deck`.
4. `render`, look at the previews as in step 5 above.

If `render` says the .pptx was changed after the last render, the user edited it in PowerPoint. Ask what they changed, move it into `deck.yaml` (or `style.md`), then render with `--force`. Don't just force it: their edits would be lost.

### Changing a style

Edit `styles/{name}/style.md` and run `sample {name}`. Existing decks keep their own copy and don't change. To bring a deck along, copy the changed values into that deck's `style.md` by hand.

## Outputs

- `decks/{date}-{slug}/{slug}.pptx`: open in PowerPoint or Keynote, or upload to Google Slides.
- `decks/{date}-{slug}/preview/slide-NN.png`: Keynote's rendering, for checking. PowerPoint can differ slightly.

`decks/` is gitignored, so using this workspace never creates a commit. In Conductor workspaces it is a symlink to the main checkout, so decks survive archiving a workspace.

## Human check

- Facts and numbers on every slide, against your own material.
- Rights to every photo you didn't take yourself, and consent from the people in them.
- Open the .pptx on the computer you'll present from. Fonts it doesn't have are swapped for others.

## Not built yet

Charts (numbers are shown as `stats` or `table` for now), building on an existing .pptx/.potx template, icons, Google Slides export.
