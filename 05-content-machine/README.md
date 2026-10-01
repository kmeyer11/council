# content-machine

Laver Instagram-grafik til to konti, Vejle Boldklub (dansk) og Liverpool FC (engelsk): kampresultater fra API'et, plus skabeloner til breaking news, klubudtalelser, transfers og skadesopdateringer. Se `CONTEXT.md` for hvordan det hele hænger sammen.

## Kom i gang

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/playwright install chromium
cp .env.example .env    # indsæt API_FOOTBALL_KEY og FOOTBALL_DATA_KEY
.venv/bin/python -m content_machine.cli teams --search Vejle   # sæt api.team_id i clubs/vejle.yaml
```

## Brug

```bash
.venv/bin/python -m content_machine.cli match --club vejle                      # seneste kamp: bekræft at det er den rigtige → post.png
.venv/bin/python -m content_machine.cli new transfer --club liverpool --slug x   # start et opslag fra skabelon
.venv/bin/python -m content_machine.cli render posts/…/post.yaml                 # tegn igen efter rettelser
```
