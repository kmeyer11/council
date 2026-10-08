# match-predictor

One job: predict the next round of a football league. A Dixon-Coles model gives the base win/draw/loss odds, and current team news adjusts them. The output is probabilities, not certainties.

## Inputs

- Working (this run): the league slug, one of `premier-league`, `la-liga`, `bundesliga`, `champions-league`, `world-cup`, `danish-superliga` (defined in `match_predictor/config.py`, run `leagues` to list them).
- Reference (every run): `.env`, which holds `FOOTBALL_DATA_KEY` (football-data.org) and an optional `THESPORTSDB_KEY` (needed only for the Danish Superliga). These are secrets: never commit them. See `.env.example`.
- Reference (every run): `../00-shared/conventions.md`

Do NOT load: `data/match_predictor.db` as text. It is a SQLite file, so query it with `sqlite3`.

## Process

1. Run commands from this folder with the venv's Python (`.venv/bin/python`). Create the venv first if it is missing: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
2. Refresh the results: `.venv/bin/python -m match_predictor.cli fetch --league {slug}`. The local DB only knows matches up to the last fetch, so a stale DB means stale strengths.
3. Get the base model: `.venv/bin/python -m match_predictor.cli predict --league {slug}`.
4. Add team news (agent): search for injuries, suspensions, players returning from international duty, and managerial changes for every club in the round. Move the model numbers only a few points, and give a stated reason for each change. Keep the model and adjusted numbers side by side.
5. **Distrust thin data.** Newly promoted teams, and the first rounds of a season, give extreme numbers (for example, 6% home-win chances). Move those toward 33/33/33 and say so.

## Outputs

- The chat: a table with Fixture | Model H/D/A | Adjusted H/D/A | Pick + score | Confidence | Reason, with sources for the news claims.
- `data/match_predictor.db`, which caches the finished results, so it is safe to re-fetch.

## Human check

Re-check the confirmed line-ups about an hour before kick-off. Injury reports conflict often, and a key player starting can flip a pick.
