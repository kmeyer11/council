# skum-og-sandhed

Røvernes øl-arkiv: en liste over øl vennerne har smagt, med deres egen rating ved siden af Untappd. Data kommer fra et Google Sheet.

## Hvor koden bor

Ikke her. Den rigtige app ligger i sit eget repo, `~/Github/skum-og-sandhed` (ASP.NET Razor Pages, kører i Docker på localhost:8008).

- UI: `Client/Pages/Index.cshtml`, `Client/Pages/Shared/_Layout.cshtml`, `Client/wwwroot/css/site.css`
- Tabellen er DataTables (jQuery) mod `GET /api/beers`; klik på en række åbner en Bootstrap-modal
- Felter pr. øl: navn, bryggerier, bryg-år, druk-år, ABV, gæring, gærtype, pris, Røvernes rating, Untappd-rating, food pairing, beskrivelse, humle, malt, adjuncts, typer

## Denne mappe

`mockups/` er designretninger med falske data (`mockups/data.js`), kun front-end. Den valgte mockup er referencen for, hvordan `Client/` skal se ud. Ingen brand-assets fra `../../assets/` endnu; sitet har sin egen identitet.
