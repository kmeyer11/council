# job-search

Skræddersyr CV og følgebrev til et konkret jobopslag, og holder øje med nye opslag på Jobindex og Jobnet. Se `CONTEXT.md` for hvordan det hele hænger sammen.

## Kom i gang

1. Læg dit master-CV og følgebrev i `profile/` som `cv.docx` og `foelgebrev.docx`.
2. Udfyld `profile/rammer.md` (og evt. `profile/erfaringsbank.md`) — skabeloner ligger i `templates/`.
3. Kopiér `templates/criteria.yaml` til `config/criteria/{emne}.yaml` og udfyld.

## Skræddersy en ansøgning

Giv agenten et jobopslag (URL eller tekst): "lav en ansøgning til det her".

## Kør jobovervågningen

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # første gang
.venv/bin/python -m job_watch.cli
```

Nye opslag lander i `state/jobs.csv`. (Ingen cron sat op endnu.)
