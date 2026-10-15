# Council

An umbrella over your workspaces: one shared rule set (`00-shared/`), one numbered folder per workspace, each self-contained enough that any AI assistant can open it and work effectively without asking you first.

Built on ICM: folders carry sequencing, hierarchy carries context, files carry state. The structure is the documentation — if something needs explaining, the explanation goes in that folder's `CONTEXT.md`, not in your head.

## Where things live

| Folder | What it holds |
|---|---|
| `00-shared/` | factory: rules that apply to every workspace (comment style, conventions) — edit here, not per-workspace |
| `02-vinted-watch/` | vinted.dk watcher: searches for anything matching your saved criteria (started as books, now any category), favourites and logs matches |
| `03-website-making/` | brand assets (logos, fonts, images, colors, voice) reused across website projects, each project self-contained under `sites/` |
| `04-job-search/` | tailors CV + cover letter to a specific job posting within your own rules, and watches Jobindex/Jobnet for new postings |
| `07-roverne/` | media for Røverne (Danish rover clan): invitation templates rendered to PNG/PDF from your own photos, saved to an iCloud folder |

Full roster with status lives in `CONTEXT.md` — this table only routes.

## Route by what just happened

| If | Go to | Then stop at |
|---|---|---|
| doing homelab work (debug, add a service, check setup) | [`~/Github/homelab`](https://github.com/kmeyer11/homelab) (its own repo, own `CONTEXT.md`) | not part of Council — cloned separately |
| making a BVB Instagram post (match result, breaking news, statement, transfer, injury) for `@bvb.immer.weiter` | [`~/Github/content-machine`](https://github.com/kmeyer11/content-machine) (its own repo, own `CONTEXT.md`) | not part of Council — cloned separately |
| running vinted-watch, or adding a new search topic/theme | `02-vinted-watch/CONTEXT.md` | read it, then `02-vinted-watch/config/topics/` and `config/criteria/` |
| adding/updating a brand asset, or starting/building a website | `03-website-making/CONTEXT.md` | read it, then `03-website-making/assets/` and the relevant `sites/{slug}/` |
| tailoring an application to a job posting, changing application rules, or running the job watch | `04-job-search/CONTEXT.md` | read it, then `04-job-search/profile/` and the relevant `applications/{slug}/` or `config/criteria/` |
| making an invitation ("lav en invitation") or other media for Røverne, or adding a template | `07-roverne/CONTEXT.md` | read it, then follow `07-roverne/templates/{type}/opskrift.md` (it asks the user for the content) |
| unsure how to comment/format code for any workspace here | `00-shared/conventions.md` | apply it, don't restate it elsewhere |
| adding a new workspace to Council | copy the next free number + the shape of `02-vinted-watch/` | new folder gets its own `CONTEXT.md`, add a row here and in `CONTEXT.md` |

## The one rule

Facts live in exactly one file. If a setup fact changes, edit it where it lives — don't copy it into a note or a chat.
