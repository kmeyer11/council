# website-making — brand assets + site projects

One job: hold the brand assets (logos, fonts, images, colors, voice) so any website you build can pull from one place instead of re-uploading files or re-describing the brand every time, and give each individual site its own self-contained project folder underneath.

`assets/vendor/` is the one exception to "brand material only" — shared third-party code libraries (e.g. GSAP) that more than one site pulls from, kept out of `sites/{slug}/` for the same reuse reason as logos/fonts/images.

## Inputs

- Reference (every task): `assets/brand.md` — colors, typography, logo usage, voice/tone
- Reference (every task): `assets/logos/`, `assets/fonts/`, `assets/images/` — the actual asset files
- Reference (every task): `../00-shared/conventions.md` — global rules (comments, style)
- Working (per site): `sites/{slug}/` — that site's own code/content, once it exists
- Working (per site, pre-build): `sites/{slug}/mockups/` — design approaches for that site, before any real build starts

Do NOT load: asset binaries (images, fonts) as text — reference them by path, don't try to read their contents. Don't load other sites under `sites/` when working on one — each is scoped to itself.

## Process

1. **Adding/updating a brand asset**: drop the file in the right `assets/` subfolder, then update `assets/brand.md` with the facts about it (hex codes, font family/weight, usage rule) if they're not obvious from the filename alone.
2. **Starting a new website — mockup gate, before anything else**: no backend, data wiring, auth, or API calls until a design direction is approved. Produce the mockup(s) with the `design` skill (a visual canvas — draft a few artboards as different approaches side by side, the user clicks/edits/compares) unless a plain static page is a better fit, in which case hand-write static HTML/CSS into `sites/{slug}/mockups/` instead. Either way: front-end only, fake/placeholder content is fine, nothing wired to real data. Ask explicitly which direction to run with (or whether to iterate) before moving on — don't infer approval from silence or from "looks good" about something else.
3. **After approval**: create/continue `sites/{slug}/`, pull what's needed from `assets/` (reference it directly, or copy in if the build needs a local copy — say which and why). Framework/stack choice lives in that site's own folder, not here. The approved mockup is the reference for how the real build should look — check back against it, don't drift.
4. **Building/editing a site**: work inside `sites/{slug}/`. Treat `assets/` as the single source of truth for brand material — don't let a second, drifting copy of a logo or color value accumulate inside a site folder.

## Outputs

- `sites/{slug}/mockups/` — design explorations, kept even after approval as a record of what was chosen and what was passed over
- `sites/{slug}/` — each website project's actual code and content
- `assets/` stays reference-only; it's not generated or modified by any site's build output

## Human check

You're the one who knows whether a color, font, or logo file is actually current — if `assets/brand.md` looks stale against the real files, that's a signal to fix the file, not route around it. For a built site, preview it running before calling a change done (Claude can't confirm visual correctness without seeing it render). For a new site, you're the approval gate on the mockup before any backend work starts — say "go with this one" (or similar) explicitly; that's what unblocks step 3.
