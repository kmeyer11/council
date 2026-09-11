# orkester — the umbrella

The unit here is an agent (or agent-fed knowledge folder), not a pipeline run. Each one is self-contained; they share only the reference layer.

| Agent folder | What it's for | Status |
|---|---|---|
| `homelab/` | keeps your homelab setup (hardware, network, services) so any assistant can pick up context without a briefing | active |

Factory (stable, shared by every agent): `_shared/conventions.md`
Product (owned per-agent): each folder's own contents — `homelab/setup/` for the homelab agent.

Status is whatever exists: an agent folder is active once it has its own `CONTEXT.md` and at least one real file underneath — not just a placeholder.

Adding agent #2: copy the shape of `homelab/` (a `CONTEXT.md` contract + a `setup/` or equivalent folder for its facts), give it its own row above, and route to it from the root `CLAUDE.md`.
