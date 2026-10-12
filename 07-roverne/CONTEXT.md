# roverne

Makes media for Røverne, a Danish rover clan (roverklan): invitations first, more templates as they're needed. Everything is in Danish. Media is rendered from HTML/CSS with headless Chromium as PNG (to share on Instagram, Facebook, Messenger) and/or PDF (to print).

## Inputs

- `brand/brand.yaml`: name, tagline, colours, fonts, logo (`brand/logo.png`, one colour, recoloured per background), and `background` (`brand/skov.jpg`, blurred behind any piece without its own `photo`). Every template takes its look from here. **The colours are placeholders** until the user gives the real ones.
- `config.yaml`: `output_dir`, the iCloud Drive folder finished media goes in. Written with `~` so it's the same on every Mac on the same iCloud account.
- `photos/`: photos the user wants to use, in any subfolders (e.g. `photos/sommerlejr-2026/`). JPG, PNG, WebP or HEIC (straight from an iPhone; converted to JPG in `photos/.converted/` at render time). Gitignored: these are photos of real people.
- `templates/{type}/example.yaml`: every field a template takes, with comments. `templates/{type}/template.html`: the layout. `templates/{type}/opskrift.md`: the recipe the agent follows to make one (questions to ask, then the draft).
- Reference (every task): `../00-shared/conventions.md`

Do NOT load images as text. Use `photos` to list them by name. Only open a photo to view it when the user asks you to pick one by what's in it.

## Process

All commands run from this folder with `.venv/bin/python -m roverne.cli …`. Setup once: `uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt && .venv/bin/playwright install chromium` (Conductor's setup script does this).

### Making an invitation

When the user says "lav en invitation" (or similar), follow `templates/invitation/opskrift.md`. It covers the questions to ask, the draft, rendering, and changes. In short: `new invitation --slug {short-name}` → fill in `source.yaml` (fields in `templates/invitation/example.yaml`) → `render "{path}/source.yaml"` → look at every file → edit the yaml and render again.

### Adding a template

Create `templates/{type}/template.html` (with `{% extends "_layout.html" %}`), `templates/{type}/example.yaml` (with `type: {type}` and `slug: example`) and `templates/{type}/opskrift.md` (copy the shape of the invitation one). Colours and fonts come from `brand` via the CSS variables in `_layout.html`. Give a text box the class `fit` plus a CSS `max-height` if long text should shrink to fit it. Render the example in every format in `render.FORMATS` before calling it done. Don't use `text-shadow`: Chromium's PDFs turn it into grey boxes.

## Outputs

- `{output_dir}/{date}-{type}-{slug}/` → `source.yaml` (data), `{slug}-post.png` / `-story.png` (share these), `{slug}-a5.pdf` / `-a4.pdf` (print these).

## Human check

- Date, time, place and the Facebook answer deadline, against the plan. The weekday is computed, so check the date itself.
- Scan the QR code with a phone before sending it out: it must open the right Facebook event.
- **Consent for every photo with people in it.** Ask before posting someone in a portrait-style photo, and never post someone who said no.

## Not built yet

Other templates (poster for recruiting, "tak for i dag" post, merch, event cover), real brand colours, a vector (SVG) logo, Instagram carousels.
