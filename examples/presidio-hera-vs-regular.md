# Presidio County, TX — HERA Special vs Regular 2 BR 60%

```bash
python3 desk/quote.py --county Presidio --state TX --br 2 --ami 60
python3 desk/quote.py --county Presidio --state TX --br 2 --ami 60 --hera
```

Regular 3-person 60% = $45,240 ($1,131/mo). HERA Special 3-person 60% = $73,860 ($1,846/mo). HERA Special applies **only** if the building was placed in service in 2007 or 2008. A 2010+ BIN must use Regular. Los Angeles is `HERA_Lim_type26=Regular` — `--hera` is a no-op there.
