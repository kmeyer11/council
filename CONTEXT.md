# Council — the umbrella

The unit here is a workspace, not a pipeline run. Each one is self-contained; they share only the reference layer. Numbering is read order / arrival order, not execution order — `00-shared/` first, then workspaces in the order they were added.

| # | Workspace folder | What it's for | Status |
|---|---|---|---|
| 00 | `00-shared/` | factory: rules every workspace follows (comments, code style, writing style) | active |
| 02 | `02-vinted-watch/` | searches vinted.dk for anything matching your saved criteria (books to start, any category now), favourites and logs matches | active, code working, cron not currently scheduled |
| 03 | `03-website-making/` | brand assets (logos, fonts, images, colors, voice) shared across website projects, each project self-contained under `sites/` | active, assets not yet filled in |
| 04 | `04-job-search/` | tailors CV + cover letter (.docx) to a job posting within your rules, and watches Jobindex/Jobnet for new postings | active, watch working; waiting on your CV/letter in `profile/`, cron not scheduled |
| 06 | `06-match-predictor/` | predicts the next round of a football league: Dixon-Coles model + agent team-news adjustment | active, moved in from `kmeyer11/match-predictor` 2026-10-08; PL data fetched through Matchday 5 |
| 07 | `07-roverne/` | media for Røverne (Danish rover clan): invitations rendered HTML→PNG/PDF into an iCloud folder | active, added 2026-10-12; output in iCloud `spejder/rover`, needs real colours and photos |

`01` is a deliberate gap — the homelab workspace moved to its own repo,
[`kmeyer11/homelab`](https://github.com/kmeyer11/homelab) (`~/Github/homelab`),
since it needs to be clonable on its own onto homelab servers without the
rest of Council. Not renumbered, to avoid re-pointing anything at `02`/`03`.

`05` is a gap too — a retired workspace, removed 2026-10-15. Not renumbered either.

Factory (stable, shared by every workspace): `00-shared/conventions.md`
Product (owned per-workspace): each folder's own contents — `02-vinted-watch/state/` for vinted-watch, `03-website-making/sites/` for website-making, `04-job-search/applications/` for job-search, `06-match-predictor/data/` for match-predictor, `output_dir` in `07-roverne/config.yaml` (iCloud Drive) for roverne.

Status is whatever exists: a workspace is active once it has its own `CONTEXT.md` and at least one real file underneath — not just a placeholder.

Adding the next workspace: pick the next free number, copy the shape of `02-vinted-watch/` (a `CONTEXT.md` contract + a folder for its facts/config), give it its own row above, and route to it from the root `CLAUDE.md`.
