# roverne

Laver medier til Røverne (roverklan): invitationer som PNG til deling og PDF til print. Færdige filer lægges i en iCloud-mappe (`config.yaml`). Se `CONTEXT.md` for hvordan det hele hænger sammen.

## Brug

```bash
.venv/bin/python -m roverne.cli new invitation --slug hike-rold-skov   # start en invitation i iCloud-mappen
.venv/bin/python -m roverne.cli render ".../source.yaml"                # tegn PNG/PDF efter rettelser
.venv/bin/python -m roverne.cli photos                                  # vis billederne i ~/Resources/spejder/rover
```

Billeder hentes fra `~/Resources/spejder/rover` (`media_dir` i `config.yaml`; HEIC fra iPhone virker). Farver og logo står i `brand/brand.yaml`.
