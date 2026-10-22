# presentations

Makes PowerPoint decks (.pptx). The finished .pptx goes on the Desktop. Its source stays here in Council, so the deck can be changed and rendered again later. A **style** is a look: colours, fonts, sizes, motif, and rules for writing slides. There is one base style, `bold`. A **deck** is one presentation. It starts from a copy of `bold`, and that copy is tailored to the talk (colours, fonts, footer, mood). The copy is the only style the deck reads, so slides added months later still match, even if `bold` has changed since.

## Inputs

- `styles/bold/style.md`: the base style every deck starts from. YAML front matter is what the renderer reads (colours, fonts, sizes, `motif`, `footer`, `logo`). The Markdown body is what you read before writing slides: mood, when to use it, rules. A logo or other file the style uses sits next to it.
- `decks/{date}-{slug}/`: one deck's source (gitignored).
  - `style.md`: a copy of `bold`, made by `new`, then tailored to this deck. It is the only style file this deck reads. Its `## This deck` section records purpose, audience, language, theme and every choice made while building. **Read it before adding slides.**
  - `deck.yaml`: the slides. The single source of truth for the content.
  - `images/`: photos used by this deck.
  - `preview/slide-NN.png`: built by `render`. Don't edit them.
  - `.rendered`: hash of the last render. It is how `render` sees edits made in PowerPoint.
- `presentations/sample.yaml`: every layout once, with every field it takes. Copy blocks from here when writing a `deck.yaml`.
- Reference (every task): `../00-shared/conventions.md`

Brand colours already defined elsewhere (e.g. Røverne in `../03-website-making/assets/brand.md`) can be copied into a deck's `style.md`. Don't link to them: a style must stand alone.

Do NOT load images or the .pptx as text. Look at `preview/*.png` to see a deck.

## Process

All commands run from this folder with `.venv/bin/python -m presentations.cli …`. Setup once: `uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt` (Conductor's setup script does this). Talk to the user in their language (usually Danish).

### Making a deck ("lav en powerpoint/præsentation")

1. Ask, in one message: purpose, audience, length (minutes), language, the content (notes, a document, or keywords), and the look: mood, colours or a brand to take them from, a logo, and fonts if they care.
2. `new --style bold --slug {short-name} --title "…"` creates the folder with a copy of `bold`.
3. Tailor the deck's `style.md` to the talk: change front matter values (colours, fonts, sizes, `motif`, `footer`, `logo`) and the body's Mood and Rules where they no longer fit. Keep fonts that ship with both macOS and Windows (Arial, Georgia, Verdana, Trebuchet MS, Times New Roman) unless the user names others; a .pptx shows its fonts only if the computer it's shown on has them. With a dark `background`, set `colors.heading` to a light colour, or column headings disappear.
4. Fill in `## This deck`. Under Decisions, list what changed from `bold` and why.
5. Write a `deck.yaml` with just the title slide and two or three content slides, `render`, and show the user the look before writing the rest.
6. Write the rest of `deck.yaml`. Roughly 1 slide per 1.5–2 minutes. Follow the deck's style rules. Vary layouts. Put what the speaker says in `notes`, not on the slide.
7. Every fact (numbers, names, dates) must come from the user's material. If one is missing, ask.
8. `render decks/{folder}`. Fix every `WARNING` (text that probably overflows), then look at every PNG in `preview/`. Fix and render again.
9. Show the user the previews and the path to the .pptx on the Desktop, plus a list of what you wrote yourself, so they can change it.

### Adding slides to a deck later

1. Read the deck's `style.md` (front matter and `## This deck`) and the whole `deck.yaml`.
2. Add the slides to `deck.yaml` in the same voice and with the same layouts. Use only what the deck's `style.md` allows.
3. If you made a new choice (a new layout, a new kind of image), add it under `Decisions` in `## This deck`.
4. `render`, look at the previews as in step 5 above.

If `render` says the .pptx on the Desktop was changed after the last render, the user edited it in PowerPoint. Ask what they changed, move it into `deck.yaml` (or `style.md`), then render with `--force`. Don't just force it: their edits would be lost.

### Changing a deck's look

Edit that deck's `style.md`, note the change under Decisions, and `render`.

### Changing the base style

Edit `styles/bold/style.md` and run `sample bold`, which renders every layout to `decks/_samples/bold/` (not the Desktop). Look at every PNG and show the user. Existing decks keep their own copy and don't change.

## Outputs

- `~/Desktop/{slug}.pptx`: open in PowerPoint or Keynote, or upload to Google Slides. If a file with that name is already there and wasn't rendered from this deck, `render` stops. Rename the file, or change `slug` in `deck.yaml`.
- `decks/{date}-{slug}/preview/slide-NN.png`: Keynote's rendering, for checking. PowerPoint can differ slightly.

`decks/` is gitignored and the .pptx sits outside the repo, so using this workspace never creates a commit. In Conductor workspaces it is a symlink to the main checkout, so decks survive archiving a workspace.

## Human check

- Facts and numbers on every slide, against your own material.
- Rights to every photo you didn't take yourself, and consent from the people in them.
- Open the .pptx on the computer you'll present from. Fonts it doesn't have are swapped for others.

## Not built yet

Charts (numbers are shown as `stats` or `table` for now), building on an existing .pptx/.potx template, icons, Google Slides export.
