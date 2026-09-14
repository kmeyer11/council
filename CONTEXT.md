# Stack — the umbrella

The unit here is a workspace, not a pipeline run. Each one is self-contained; they share only the reference layer. Numbering is read order / arrival order, not execution order — `00-shared/` first, then workspaces in the order they were added.

| # | Workspace folder | What it's for | Status |
|---|---|---|---|
| 00 | `00-shared/` | factory: rules every workspace follows (comments, code style, writing style) | active |
| 01 | `01-homelab/` | keeps your homelab setup (hardware, network, services) so any assistant can pick up context without a briefing | active |
| 02 | `02-vinted-watch/` | searches vinted.dk for anything matching your saved criteria (books to start, any category now), favourites and logs matches | active, code working, cron not currently scheduled |
| 03 | `03-website-making/` | brand assets (logos, fonts, images, colors, voice) shared across website projects, each project self-contained under `sites/` | active, assets not yet filled in |

Factory (stable, shared by every workspace): `00-shared/conventions.md`
Product (owned per-workspace): each folder's own contents — `01-homelab/setup/` for homelab, `02-vinted-watch/state/` for vinted-watch, `03-website-making/sites/` for website-making.

Status is whatever exists: a workspace is active once it has its own `CONTEXT.md` and at least one real file underneath — not just a placeholder.

Adding the next workspace: pick the next free number, copy the shape of `01-homelab/` (a `CONTEXT.md` contract + a folder for its facts/config), give it its own row above, and route to it from the root `CLAUDE.md`.
