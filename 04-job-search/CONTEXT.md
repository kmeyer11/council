# job-search

Two jobs: (1) turn your master CV + cover letter into a version tailored to one specific job posting, within rules (`rammer`) you control; (2) watch Danish job sites for new postings matching your criteria.

## Inputs

- Working (tailoring): `profile/cv.docx`, `profile/foelgebrev.docx` — the masters. Never edited by a tailoring run; each application gets its own copies.
- Working (tailoring): `profile/erfaringsbank.md` — facts, projects and results not in the CV but allowed to be used. The only other source of truth about you besides the CV.
- Working (tailoring): `profile/rammer.md` — standing rules for every application (tone, length, language, always/never). `applications/{slug}/rammer.md` — rules for one application only.
- Working (watch): `config/criteria/*.yaml` — one file per search topic. Format: `templates/criteria.yaml`.
- Reference (every run): `config/config.yaml` — active sources, `max_age_days`, geography
- Reference (every task): `../00-shared/conventions.md`
- Templates: `templates/` — starting points for `profile/rammer.md`, `profile/erfaringsbank.md`, `applications/{slug}/noter.md`, `config/criteria/*.yaml`. Copy, don't edit in place.

`profile/`, `applications/`, `state/` and `config/criteria/` are gitignored — personal content never leaves this machine via git. Don't copy it anywhere that is committed.

Do NOT load: `state/job_watch.db` as text (SQLite). Don't load other `applications/*` folders when working on one, unless asked to reuse something from a previous application.

## Process

### Tailoring an application

1. **Posting**: create `applications/{yyyy-mm-dd}-{firma}-{stilling}/` (lowercase, dashes). Save the posting as `opslag.md`: URL at the top, then the full text. If only a URL was given, fetch it; if the fetch fails or looks incomplete, ask for the text rather than working from a partial posting. A match from `state/jobs.csv` starts here with its URL.
2. **Rules, in order — later wins**: `../00-shared/conventions.md` → `profile/rammer.md` → `applications/{slug}/rammer.md` → what's said in chat this session. If a chat instruction is meant to apply from now on ("always…", "never…", "from now on…"), write it into `profile/rammer.md`; if it's for this application only, into `applications/{slug}/rammer.md`. If unclear which, ask. A rule lives in one file, not in chat memory.
3. **Analyse the posting**: must-have vs. nice-to-have requirements, key terms and their exact wording, tone (formal/informal, du/De, Danish/English), what the company says about itself. Put the short version at the top of `noter.md`.
4. **Hard rule — no invention**: select, reorder, emphasise and rephrase content that exists in `profile/cv.docx` or `profile/erfaringsbank.md`. Never add experience, numbers, tools, titles or dates that aren't there. A requirement you can't back up goes into `noter.md` under "Åbne spørgsmål" as a question to you, not into the documents.
5. **Write the documents** with the `docx` skill: copy the master `.docx` into the application folder, then edit text in place (runs/paragraphs) so layout, fonts and styles survive. Don't regenerate the document from scratch. To check the result visually on this Mac (no LibreOffice/poppler installed), render with `qlmanage -t -s 1400 -o {scratch dir} file.docx` and look at the PNG — it shows page 1 only, so also check the page count against `profile/rammer.md`. Cover letter: rewrite the body for this posting, keep the master's structure unless a rule says otherwise. CV: reorder/trim/reword sections and bullets toward the posting's requirements; keep it truthful to the master.
6. **`noter.md`** (from `templates/noter.md`): what changed vs. the master and which requirement each change answers, open questions, status line.
7. Stop and hand over for the human check. Don't iterate on your own past one draft.

### Running the watch

1. Setup once: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
2. Run from this folder: `.venv/bin/python -m job_watch.cli` (defaults: `config/config.yaml`, `state/jobs.csv`, `state/job_watch.db`)
3. Each keyword in each criteria file is searched on each source. Filters applied locally: older than `max_age_days`, any `exclude` word in the title, no `require` word in the title, and — if `locations` is set — location must contain one of them. `require` is what keeps the noise down: both sites match loosely (Jobnet splits `it-medarbejder` and effectively searches `medarbejder`; Jobindex matches boilerplate anywhere in the ad). Terms of ≤3 chars match as whole words only, longer ones also inside compounds.
4. Only postings not already in `state/job_watch.db` are reported. The same posting found on both sites (identical title + company after normalizing) is reported once.
5. **Geography** is set once in `config/config.yaml` (the `jobindex:` / `jobnet:` blocks) and applies to every criteria file; a criteria file's own block overrides key by key. Currently Odense + ~50 km incl. Fredericia — see the comment there for why Jobnet uses 52 km. Narrow at the source rather than with `locations`: Jobindex's feed only returns its 20 newest hits, so a local filter throws most of them away. Jobindex takes `address` + `radius` (or `geoareaid` read from a real jobindex.dk URL); Jobnet takes `postalCode` + `kmRadius` or `regions`. The two sites measure distance differently — when changing radius, check that the towns you care about actually show up on both. Don't guess an id.

### Adding a job site

One module in `job_watch/sources/{name}.py` with `search(client, keyword, params) -> list[Job]`, one line in `job_watch/sources/__init__.py`, and the name under `sources:` in `config/config.yaml`. Prefer an RSS feed or the JSON endpoint the site's own search page calls over HTML scraping; note in the module docstring where the endpoint came from so it can be re-found when it breaks. Verify against the live site before calling it done.

## Outputs

- `applications/{slug}/` → `opslag.md`, `cv.docx`, `foelgebrev.docx`, `noter.md`, optional `rammer.md`
- `state/jobs.csv` → appended each run with new postings (found, label, source, title, company, location, published, url)
- `state/job_watch.db` → which postings have been seen

## Human check

Tailoring: read both `.docx` files in Word before sending — check nothing got invented (cross-check `noter.md`), the layout survived, and the tone fits. Answer the open questions in `noter.md`; update its status when sent / when you hear back.

Watch: skim new rows in `state/jobs.csv`. Too much noise → add `exclude` words or narrow geography at the source. Missing obvious jobs → add keywords (both sites match free text, so synonyms and English/Danish variants matter). Jobnet's endpoint is unofficial; if a run logs `Search failed on jobnet`, see the note in `job_watch/sources/jobnet.py`.
