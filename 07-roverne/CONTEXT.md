# roverne

Makes media for Røverne, a Danish rover clan (roverklan): invitations first, more templates as they're needed. Everything is in Danish. Media is rendered from HTML/CSS with headless Chromium as PNG (to share on Instagram, Facebook, Messenger) and/or PDF (to print).

## Inputs

- `brand/brand.yaml`: name, tagline, colours, fonts, logo. Every template takes its look from here. **The colours are placeholders** until the user gives the real ones, and there's no logo yet (`logo: null`).
- `config.yaml`: `output_dir`, the iCloud Drive folder finished media goes in. Written with `~` so it's the same on every Mac on the same iCloud account.
- `photos/`: photos the user wants to use, in any subfolders (e.g. `photos/sommerlejr-2026/`). JPG, PNG, WebP or HEIC (straight from an iPhone; converted to JPG in `photos/.converted/` at render time). Gitignored: these are photos of real people.
- `templates/{type}/example.yaml`: every field a template takes, with comments. `templates/{type}/template.html`: the layout.
- Reference (every task): `../00-shared/conventions.md`

Do NOT load images as text. Use `photos` to list them by name. Only open a photo to view it when the user asks you to pick one by what's in it.

## Process

All commands run from this folder with `.venv/bin/python -m roverne.cli …`. Setup once: `uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt && .venv/bin/playwright install chromium` (Conductor's setup script does this).

### Making an invitation

1. `new invitation --slug {short-name}` creates `{output_dir}/{today}-invitation-{slug}/source.yaml` from the example.
2. Fill in `source.yaml` from what the user said. Don't invent facts (times, place, price, who to contact, what to bring). Leave a field `null` or remove it, and ask. Remove example values the user didn't give, e.g. the example's `bring` list.
   - Dates go in `starts` / `ends` as `2026-11-07` or `2026-11-07 10:00`. The weekday and month names are computed, so don't type them in `text` either.
   - A photo: `photo: photos/…` (from `photos`). Move the crop with `photo_position` (e.g. `center 30%`) if faces end up under the text.
   - `formats`: `post` 1080×1350 PNG, `story` 1080×1920 PNG, `a5` / `a4` PDF. Ask which they want if unclear. Default `[post, a5]`.
3. `render "{path}/source.yaml"`. It writes `{slug}-{format}.png/.pdf` next to the yaml.
4. Look at every PNG (and the PDF if printing) before handing it over. A warning that content is cut off means: shorten `text` or `bring`, or drop that format. The `post` format has the least room.
5. Changes: edit `source.yaml` and render again. The yaml is the single source of truth for that piece.

### Adding a template

Create `templates/{type}/template.html` (with `{% extends "_layout.html" %}`) and `templates/{type}/example.yaml` (with `type: {type}` and `slug: example`). Colours and fonts come from `brand` via the CSS variables in `_layout.html`. Give a text box the class `fit` plus a CSS `max-height` if long text should shrink to fit it. Render the example in every format in `render.FORMATS` before calling it done. Don't use `text-shadow`: Chromium's PDFs turn it into grey boxes.

## Outputs

- `{output_dir}/{date}-{type}-{slug}/` → `source.yaml` (data), `{slug}-post.png` / `-story.png` (share these), `{slug}-a5.pdf` / `-a4.pdf` (print these).

## Human check

- Date, time, place and signup deadline, against the plan. The weekday is computed, so check the date itself.
- Scan the QR code with a phone before sending it out.
- **Consent for every photo with people in it.** Ask before posting someone in a portrait-style photo, and never post someone who said no.

## Not built yet

Other templates (poster for recruiting, "tak for i dag" post, merch, event cover), a real logo and brand colours, Instagram carousels.
