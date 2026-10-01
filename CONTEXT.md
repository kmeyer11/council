# Council — the umbrella

The unit here is a workspace, not a pipeline run. Each one is self-contained; they share only the reference layer. Numbering is read order / arrival order, not execution order — `00-shared/` first, then workspaces in the order they were added.

| # | Workspace folder | What it's for | Status |
|---|---|---|---|
| 00 | `00-shared/` | factory: rules every workspace follows (comments, code style, writing style) | active |
| 02 | `02-vinted-watch/` | searches vinted.dk for anything matching your saved criteria (books to start, any category now), favourites and logs matches | active, code working, cron not currently scheduled |
| 03 | `03-website-making/` | brand assets (logos, fonts, images, colors, voice) shared across website projects, each project self-contained under `sites/` | active, assets not yet filled in |
| 05 | `05-content-machine/` | Instagram post graphics for two club accounts (Vejle Boldklub DA, Liverpool FC EN): match results via API-Football + announcement templates, rendered HTML→PNG | active, first match posts rendered; match data looked up by the agent (free API plan can't serve the current season) |

`01` is a deliberate gap — the homelab workspace moved to its own repo,
[`kmeyer11/homelab`](https://github.com/kmeyer11/homelab) (`~/Github/homelab`),
since it needs to be clonable on its own onto homelab servers without the
rest of Council. Not renumbered, to avoid re-pointing anything at `02`/`03`.

Factory (stable, shared by every workspace): `00-shared/conventions.md`
Product (owned per-workspace): each folder's own contents — `02-vinted-watch/state/` for vinted-watch, `03-website-making/sites/` for website-making, `05-content-machine/posts/` for content-machine.

Status is whatever exists: a workspace is active once it has its own `CONTEXT.md` and at least one real file underneath — not just a placeholder.

Adding the next workspace: pick the next free number, copy the shape of `02-vinted-watch/` (a `CONTEXT.md` contract + a folder for its facts/config), give it its own row above, and route to it from the root `CLAUDE.md`.
