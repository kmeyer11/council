# vinted-watch

One job: check vinted.dk for new listings matching your search criteria — any category, not just books — favourite them, and log matches. Precisely, not exhaustively.

## Inputs

- Working (this run): `config/criteria/*.yaml` — concrete search terms, one file per topic/list. Each has `label:` and `terms:` (a flat list of strings — specific titles, authors, product names, anything searchable), and can optionally override `catalog_ids` / `price_from` / `price_to` / `order` / `per_page` from `config.yaml` for just that file (e.g. a non-book topic in a different category or price range).
- Working (before criteria exists): `config/topics/*.md` — free text describing what you want. Not read by the code; it's a paper trail of the ask, useful for whoever turns it into `criteria/*.yaml`. It can be written by you, or by the agent directly from a chat request ("I want to look for Nike sneakers") — either way, write it before writing the criteria file, don't skip straight to criteria with no record of what was asked.
- Reference (every run): `config/config.yaml` — domain, default catalog id/price bounds (every criteria file inherits these unless it overrides them), `dedup_threshold`
- Reference (every run): `.env` — `VINTED_COOKIE` / `VINTED_CSRF_TOKEN`, needed only for `--favorite`. Secret — never commit, never move outside this folder without thinking about it.
- Reference (every run): `../00-shared/conventions.md`

Do NOT load: `state/vinted_watch.db` as text — it's a SQLite file, not something to read directly.

## Process

### Turning a topic into criteria (you, or ask me — including straight from chat)

1. Write what's wanted to `config/topics/{slug}.md` — a specific item, a list of items, or a loose category/theme ("books about world war 2", "black leather boots size 42", "Nike sneakers").
2. If it's already specific items, `criteria/{slug}.yaml` is close to a straight copy. If it's a theme, expand it into a real, concrete list of search terms — the search itself is plain text matching, it can't search "by theme," only by what's actually in a listing's title. Prefer a shorter list of terms you're confident are accurate over a long list of guesses.
3. **If the topic isn't books:** `config.yaml`'s default `catalog_ids` (2312, Bøger) will silently restrict the search to books unless overridden. Do not guess a category id — a wrong number is worse than none, since it silently returns zero/wrong results instead of erroring. Either look up the real id (browse the category on vinted.dk and read it out of the URL, e.g. `.../catalog/1231-shoes`) and set it, or leave `catalog_ids` out of the criteria file entirely — that searches across every category, which is a safe, correct default, just less targeted. Say which you did.
4. Write the result to `config/criteria/{slug}.yaml`. Minimal (inherits category/price from `config.yaml`):
   ```yaml
   label: WW2
   terms:
     - Anne Franks dagbog
     - Bogtyven
   ```
   With an override, once a real category id is known (example only — verify the actual number, don't reuse this one):
   ```yaml
   label: Sneakers
   catalog_ids: "{id from the category URL}"
   price_to: 400
   terms:
     - Nike Air Max
   ```
5. **Read it before the next run.** This is agent-generated text — spelling/translation mistakes or an unverified category id are the most likely failure modes. Edit the file directly if something's off; nothing else needs to change.

### Running the watch

1. Run from this folder: `python -m vinted_watch.cli --config config/config.yaml --favorite --csv state/matches.csv --db state/vinted_watch.db`
2. It only reports items not already in `state/vinted_watch.db` — safe to run repeatedly (cron, launchd, or by hand).
3. **Duplicate listings of the same item** (different seller, slightly different title text) are detected by fuzzy-matching the normalized title against everything already seen, and skipped — logged as seen so they don't resurface, but not reported or favourited. Tune strictness via `dedup_threshold` in `config.yaml` (0–1, higher = stricter, catches fewer near-duplicates). Default 0.84 is tuned toward fewer, more precise hits over exhaustive coverage — see `vinted_watch/dedupe.py` if it's too aggressive or not aggressive enough.
4. If `.env` is missing or stale (cookie/token expired), matches still get found and logged, they just won't be favourited — see `README.md` for how to refresh it.

## Outputs

- `state/matches.csv` → appended each run with new matches
- `state/vinted_watch.db` → tracks what's already been seen (by listing id) and every normalized title seen (for duplicate detection)

## Human check

Skim new rows in `state/matches.csv` (or the favourited items on vinted.dk) — the search is fuzzy on Vinted's side, so an occasional off-topic match is expected, not a bug. If duplicates of the same item are still slipping through, lower `dedup_threshold` a bit; if a genuinely different item gets skipped as a false-positive duplicate, raise it.
