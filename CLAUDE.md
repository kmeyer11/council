# orkester

An umbrella over your agents: one shared rule set (`_shared/`), one folder per agent, each folder self-contained enough that any AI assistant can open it and work effectively without asking you first.

Built on ICM: folders carry sequencing, hierarchy carries context, files carry state. The structure is the documentation — if something needs explaining, the explanation goes in that folder's `CONTEXT.md`, not in your head.

## Where things live

| Folder | What it holds |
|---|---|
| `_shared/` | factory: rules that apply to every agent (comment style, conventions) — edit here, not per-agent |
| `homelab/` | the homelab agent's knowledge: hardware, network, services, conventions |

## Route by what just happened

| If | Go to | Then stop at |
|---|---|---|
| doing homelab work (debug, add a service, check setup) | `homelab/CONTEXT.md` | read it, then the setup files it points to |
| unsure how to comment/format code for any agent here | `_shared/conventions.md` | apply it, don't restate it elsewhere |
| adding a new agent to orkester | copy the `homelab/` shape as a starting point | new folder gets its own `CONTEXT.md` |

## The one rule

Facts live in exactly one file. If a setup fact changes, edit it where it lives — don't copy it into a note or a chat.
