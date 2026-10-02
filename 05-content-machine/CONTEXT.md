# content-machine

Makes Instagram post graphics for one account, VfB Stuttgart (German, `@vfb.ross`, `clubs/vfb.yaml`). Nothing is club-specific: a club is one yaml file plus one media folder, and a post type is one template folder that works for every club.

Built so far: match result (from API-Football), breaking news, club statement, transfer, injury update. All are rendered as 1080×1350 PNGs (Instagram 4:5) from HTML/CSS with headless Chromium.

## Inputs

- `clubs/{club}.yaml`: name, language, handle, API team id, colours, fonts, logo. It also holds `team_names` / `competition_names` / `round_names` (API spelling → how the account writes it), `competition_logos` (shown competition name → logo path) and `strings` (every word a template prints, in the club's language). If a template needs a new word, add it to **every** club's `strings`, because missing keys fail the render.
- `media/{club}/players.yaml`: slug → name, number, aliases, display name. The slug is also the photo folder name.
- `media/{club}/players/{slug}.jpg`, or several in `players/{slug}/` (one picked at random): player photos. Use portrait crops at least 1080 px wide with the face in the upper third, since the bottom half sits under the scoreboard and text.
- `media/{club}/default-bg.{jpg,png}`: optional fallback background. Without one, posts use a gradient in the club colours.
- `media/{club}/credits.yaml`: photographer + licence per photo (path → `credit` line). When a post uses a CC BY / CC BY-SA photo, its `credit` goes in the caption.
- `media/{club}/loss/`, `serious/`, `victory/`: mood photo pools (optional, any club). See **Backgrounds** below.
- `media/crests/`: crests cached from the API as `{team_id}.png` (API-Football) or `fd-{id}.png` (football-data.org); the extension follows the download URL, so SVG crests stay `.svg`. All 18 Bundesliga crests come from `crests --competition BL1` (rerun each new season, since promoted clubs change). Our own crest is the club yaml's `logo`, which wins over the API crest. The footer shows only the handle, with no logo: account logos tested 2026-10-01 were unreadable at footer size.
- `media/competitions/`: competition logos, named in the club yaml's `competition_logos`. The match graphic shows them on a white badge in the top line, because most of them are dark on white. Downloaded once with curl: Bundesliga `https://crests.football-data.org/BL1.png`, Champions League `…/CL.png`, DFB-Pokal / Europa League / Conference League `https://media.api-sports.io/football/leagues/{81,3,848}.png` (plain downloads, no key). A competition without a logo shows text only.
- `.env`: `API_FOOTBALL_KEY` and `FOOTBALL_DATA_KEY` (see `.env.example`).
- Reference (every task): `../00-shared/conventions.md`

`posts/`, player and mood photos, crests and competition logos are gitignored. Photos are usually someone else's copyright, so they stay on this machine.

Do NOT load images as text. Don't load other `posts/*` folders when working on one post.

## Process

All commands run from this folder with `.venv/bin/python -m content_machine.cli …`. Setup once: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/playwright install chromium`.

### Match result

**Current mode: agent lookup.** The free API-Football plan can't serve this season, and the free alternatives either block scripts (ESPN, Sofascore's API), lack goal timelines (TheSportsDB, checked for the Danish league only, not yet for the Bundesliga), or give only the score (football-data.org); checked 2026-10-01. With a paid key, use the API flow below instead. Templates and posts are the same either way.

**Bundesliga or Champions League:** steps 1 and 4 can start from the API flow below. `vfb.yaml` uses the `footballdata` source, so `match` finds the match and writes `post.yaml` with the date, teams, score, round and crests. The free plan has no goals, red cards or venue, so it writes `goals: []` and doesn't render. It counts as one source for the score only. Goals and red cards still come from step 2 (then rerun `background`), and the checkpoint in step 3 still applies. The DFB-Pokal is not covered, so a cup match won't show up as the latest match.

#### Agent lookup (now)

1. Find the club's latest finished match by checking a fixtures page (fotmob, vfb.de, kicker.de), not just search snippets, because snippets lag behind.
2. Get the score, competition + round, and every goal (minute, scorer, side, pen/og) and red card from **two independent sources**. Read the sides from a page that groups scorers by team. A running score like "0-1" in a snippet is easy to misread.
3. **Checkpoint.** Show the user the date, opponent, score, goals, red cards, background choice, and the sources. Say plainly what no source mentioned (e.g. "no red cards mentioned" is not "no red cards"). Write nothing until the user confirms.
4. `new match-result --club {club} --slug {opponent} --date {match day}`, then fill `post.yaml`:
   - Our side's `crest:` is the club yaml's `logo`. A Bundesliga opponent's crest is already in `media/crests/fd-{id}.png` (ids: `teams --search "{name}" --source footballdata`). Anyone else: `crest --search "{name}"` prints the path (free plan). If several teams match (e.g. "Stuttgart II" and "Stuttgarter Kickers"), it lists them; rerun with `--id` for the first team, not a youth or women's side.
   - Names are written the way the account writes them (`display` in `players.yaml` for our players).
   - `venue:` only if a source gave it.
   - When score and goals are in, run `background posts/…/post.yaml` (see **Backgrounds**).
5. `render posts/…/post.yaml` and show the PNG.

#### API flow (needs a paid API-Football key)

1. `match --club {club}` fetches the club's most recent finished match. To pick a specific match, use `--fixture ID`.
2. **Checkpoint: confirm it's the right game.** Nothing is written until a human confirms the match (date, teams, score, competition). The API's "latest" can be a friendly, a cup game you didn't mean, or a stale result.
   - In a terminal: it asks `[y/N]`. Answering no lists the 5 most recent finished matches to pick from.
   - Run by the agent (no terminal): it prints the match and the list, then stops with "Not confirmed". Show both to the user, wait for their answer, then rerun with `--fixture ID --yes`. Never pass `--yes` unless the user confirmed that fixture in this session.
3. It writes `posts/{club}/{date}-match-{opponent}/post.yaml`. The file holds the score, goals (minute, scorer, `pen`/`og`) and red cards (straight red or second yellow). Shootout kicks and missed penalties are left out.
4. Background is picked by result (see **Backgrounds**) and written to `background:` in the yaml.
5. It renders `post.png` next to the yaml. An existing `post.yaml` is never overwritten without `--force`, because it may contain manual edits.
6. Fixing something (wrong name, different photo, add `headline: Derbysieg`): edit `post.yaml`, then run `render posts/…/post.yaml`. The yaml is the single source of truth for that post. A wrong or short-form opponent name ("M'gladbach") means the club yaml needs a `team_names` line. That fixes every future post.

### Backgrounds

`media.pick_background` picks from the post's data, and the pick is written to `background:` so re-renders don't reshuffle:

- Match result, **loss** (a shootout decides a level score): random photo from `loss/`.
- Match result, **win**: photo of whoever scored most for us. A tie is decided at random, and scorers without a photo are skipped. If no scorer has a photo, a random photo from `victory/`.
- Match result, **draw**: nothing is picked. **Ask the user which photo to use** (at the step 3 checkpoint), then write it to `background:` by hand. `background` never overwrites a draw's line, and `match` stops before rendering a draw.
- **breaking-news, statement**: random photo from `serious/`. Transfer and injury stay `null`, because their photo should be the player in question.
- Nothing found: `default-bg`, else the club gradient.

`match` and `new` pick automatically. A match post filled in by hand needs `background posts/…/post.yaml` after the score and goals are in. Rerun it to get a different random pick.

### Announcements (breaking-news, statement, transfer, injury)

1. `new {type} --club {club} --slug {short-name}` copies `templates/{type}/example.yaml` to `posts/{club}/{today}-{type}-{slug}/post.yaml`. The comments in the example explain each field.
2. Fill in the yaml from what the user said, in the club's language. Don't invent facts (fees, contract lengths, injury details). Leave a field `null` and ask.
3. `render posts/…/post.yaml`, then look at the PNG before handing it over.

### Adding a club

1. Copy one of the `clubs/*.yaml` files.
2. Set `api.team_id` with `teams --search "{name}"`. Don't guess an id.
3. Translate `strings` into the club's language.
4. Create `media/{club}/players.yaml`.

### Adding a post type

Create `templates/{type}/template.html` (with `{% extends "_layout.html" %}`) and `templates/{type}/example.yaml` (with `type: {type}`). Every visible word comes from `s.*` (club strings) or the post yaml. Give a text box the class `fit` if long text should shrink to fit it. Shrinking only checks height when the box has a CSS `max-height`. Render the example for every club in `clubs/` before calling it done.

### Data source

`content_machine/sources/apifootball.py`, API-Football v3. The free plan allows 100 requests/day; one `match` run uses 2 API requests (plus 1 per other match you pick from the list); crests are plain downloads and don't count. **The free plan only serves seasons 2022–2024 (checked 2026-10-01), so it cannot fetch current matches.** `teams` and `/players/squads` do work on it. A current-season `match` fails with `Free plans do not have access to this season`. `content_machine/sources/footballdata.py`, football-data.org v4: 10 requests/minute, current season, but on the free plan only the Bundesliga and Champions League (of what VfB plays; not the DFB-Pokal) and only the score. Goals, bookings and venue are `null` (checked 2026-10-01). Its team ids differ from API-Football's, so its crests are cached as `media/crests/fd-{id}.png`. Use `teams --source footballdata` for its ids. It has no search endpoint, so the search only looks through Bundesliga and CL teams, and `crests --competition {code}` uses the same competition team list. It uses short names ("M'gladbach", "Atleti"), which get mapped in the club yaml's `team_names`.

A different provider means a new module with the same functions (`make_client`, `recent_finished`, `fixture`, `search_teams`), one line in `sources/__init__.py`, and `api.source` in the club yaml.

## Outputs

- `posts/{club}/{date}-{type}-{slug}/` → `post.yaml` (data), `post.html` (open in a browser to tweak layout), `post.png` (upload this)

## Human check

- Score, minutes and red cards against the official match report. API data can be late or corrected after the final whistle.
- Look at the PNG: photo crop (face not hidden behind text), long names readable, right club colours/handle.
- **Rights to every photo you post.** Club and agency press photos (Getty, Ritzau, etc.) are copyrighted and get taken down or claimed on Instagram. Prefer your own photos or ones you have explicit permission for.

## Not built yet

Season-breakdown carousel (multi-slide), stories (1080×1920), captions + hashtags, short-form video (recording an animated version of these templates, or Remotion). Each new format is a new template folder; video would add a `video.py` next to `render.py`.
