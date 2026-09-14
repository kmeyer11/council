# Stack

An umbrella over your workspaces: one shared rule set (`00-shared/`), one numbered folder per workspace, each self-contained enough that any AI assistant can open it and work effectively without asking you first.

Built on ICM: folders carry sequencing, hierarchy carries context, files carry state. The structure is the documentation — if something needs explaining, the explanation goes in that folder's `CONTEXT.md`, not in your head.

## Where things live

| Folder | What it holds |
|---|---|
| `00-shared/` | factory: rules that apply to every workspace (comment style, conventions) — edit here, not per-workspace |
| `01-homelab/` | the homelab workspace: hardware, network, services, conventions |
| `02-vinted-watch/` | vinted.dk watcher: searches for anything matching your saved criteria (started as books, now any category), favourites and logs matches |
| `03-website-making/` | brand assets (logos, fonts, images, colors, voice) reused across website projects, each project self-contained under `sites/` |

Full roster with status lives in `CONTEXT.md` — this table only routes.

## Route by what just happened

| If | Go to | Then stop at |
|---|---|---|
| doing homelab work (debug, add a service, check setup) | `01-homelab/CONTEXT.md` | read it, then the setup files it points to |
| running vinted-watch, or adding a new search topic/theme | `02-vinted-watch/CONTEXT.md` | read it, then `02-vinted-watch/config/topics/` and `config/criteria/` |
| adding/updating a brand asset, or starting/building a website | `03-website-making/CONTEXT.md` | read it, then `03-website-making/assets/` and the relevant `sites/{slug}/` |
| unsure how to comment/format code for any workspace here | `00-shared/conventions.md` | apply it, don't restate it elsewhere |
| adding a new workspace to Stack | copy the next free number + the shape of `01-homelab/` | new folder gets its own `CONTEXT.md`, add a row here and in `CONTEXT.md` |

## The one rule

Facts live in exactly one file. If a setup fact changes, edit it where it lives — don't copy it into a note or a chat.
