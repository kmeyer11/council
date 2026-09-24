# vinted-watch

Finder nye opslag på vinted.dk der matcher `config/criteria/*.yaml` (bøger, eller enhver anden kategori), og favoriserer dem. Se `CONTEXT.md` for hvordan søgekriterier og dublet-filtrering virker.

## Kør

```bash
source .venv/bin/activate
python -m vinted_watch.cli --config config/config.yaml --favorite --csv state/matches.csv --db state/vinted_watch.db
```

Rediger `config/criteria/*.yaml` og `config/config.yaml` direkte for at ændre søgninger/pris/kategori.

## Ryd favoritter

```bash
python -m vinted_watch.clear_favourites --db state/vinted_watch.db --yes
```

Rører kun ting scriptet selv har fundet og favoriseret (sporet i `state/vinted_watch.db`) - ikke noget du selv har favoriseret manuelt. Tilføj `--all-favourites` for at fjerne alt.

## Hvis `.env` skal opdateres (cookie/token udløbet)

1. Log ind på vinted.dk → DevTools (F12) → Network → Fetch/XHR
2. Favoritisér et vilkårligt opslag → find requestet til `user_favourites/toggle`
3. Kopiér `cookie`-header ind i `VINTED_COOKIE` i `.env`
4. Kopiér `x-csrf-token`-header ind i `VINTED_CSRF_TOKEN` i `.env`

## Kør periodisk

```cron
*/15 * * * * cd /Users/kmeyer/Github/council/02-vinted-watch && .venv/bin/python -m vinted_watch.cli --config config/config.yaml --favorite --csv state/matches.csv --db state/vinted_watch.db >> state/run.log 2>&1
```

(Ikke aktiveret endnu — ingen cron-job kører i øjeblikket.)
