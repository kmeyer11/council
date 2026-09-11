# homelab — the setup, always loaded

One job: let any assistant know your homelab setup without you re-explaining it every time.

## Inputs

- Reference (every task): `setup/hardware.md` — what physical/virtual machines exist
- Reference (every task): `setup/network.md` — topology, addressing, DNS
- Reference (every task): `setup/services.md` — what's running, on what port, where
- Reference (every task): `../00-shared/conventions.md` — global rules (comments, style)

Do NOT load: nothing else exists here yet — keep it that way until a second real category of fact shows up.

## Process

1. Read the three `setup/` files before doing any homelab task — they're small on purpose, this should be cheap.
2. Do the task (debug, add a service, answer a question about the setup).
3. If a fact changed (new service, new device, network change), edit the relevant `setup/` file in place. Don't leave the change only in chat.

## Outputs

None as artifacts — this folder's "output" is an accurate `setup/`. Updates happen in place.

## Human check

Before trusting a fact from here, you (the human) know it's accurate because you're the one who edits `setup/` — if something here is stale, that's a signal to fix the file, not route around it.
