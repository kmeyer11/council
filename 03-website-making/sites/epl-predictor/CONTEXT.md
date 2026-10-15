# epl-predictor

A static dashboard that compares the epl-predictor models: who scores the most plshowet points, whether the gap is luck, how seasons play out, and what each model bets next.

## Where the code lives

Not here. The dashboard ships with the predictor so anyone using that repo gets it: `~/Github/epl-predictor` ([kmeyer11/epl-predictor](https://github.com/kmeyer11/epl-predictor)), folder `site/`. `python -m epl_predictor.cli export --open` refreshes its data and opens it.

## This folder

`mockups/` holds the three design directions with a snapshot of real data (`mockups/data.js`). **A (`a-dashboard.html`) was chosen** on 2026-10-15 and is the reference for `site/`; B and C are kept as the record of what was passed over.
