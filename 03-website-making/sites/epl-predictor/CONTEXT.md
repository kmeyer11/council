# epl-predictor

A simple, fast web page that compares the epl-predictor models: who scores the most plshowet points, whether the gap is luck, how seasons play out, and what each model bets next.

## Where the code lives

The models, backtest and data live in their own repo, `~/Github/epl-predictor` (Python CLI). This folder is only the page that shows what the CLI exports.

- Model list, versions, descriptions and the `benchmark` flag: `epl_predictor/models/`
- Scoring rules and leaderboard maths: `epl_predictor/scoring.py`
- What goes into the data file: `epl_predictor/export.py`

## This folder

- `index.html`, `app.js`, `charts.js`, `style.css`: the page. Plain HTML/JS, no build step, no dependencies.
- `data.js`: generated, gitignored. Written by `python -m epl_predictor.cli export` to the folder in `SITE_DIR` (epl-predictor's `.env`). Without it the page shows how to make it.
- `mockups/`: the three directions from the mockup stage. **A (`a-dashboard.html`) was chosen** on 2026-10-15 and is the reference for the page; B and C are kept as the record of what was passed over.

To refresh the numbers, in epl-predictor: `fetch` → `backtest` (after model changes) → `predict` (before a round) → `export`. Then reload the page; open `index.html` directly or serve `03-website-making/`.

Colour rule: real models take the categorical series colours in registry order; benchmarks (market, baseline) are greys with a dash (baseline also a hollow dot), so colour stays on the models being judged.
