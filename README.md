# LIHTC MTSP Rent Desk

Offline FY2026 desk that quotes **IRC §42 rent-restricted maxes** from HUD’s official **Multifamily Tax Subsidy Project** tables (4,764 county/town rows), including **income averaging 20–80%** (updated 2026-05-18), **HERA Special** 50/60 for 2007/2008 PIS buildings, the **IRC 42(i)(8) rural floor** vs the FY2026 national non-metro 4-person VLI **$42,350**, 0–4 BR imputed household sizes under **42(g)(2)(C)**, **hold-harmless** via `--floor-il` (42(g)(2)(A)), the **26 CFR 1.42-10 UA ladder**, and the **IRC 42(d)(5)(B) 30% eligible-basis boost** from HUD 2026 QCT (14,496 tracts) + metro Small DDA (2,615 ZCTAs) + 301 nonmetro DDA counties.

## Who it's for

LIHTC / bond underwriters, HFA analysts, and property managers who still take 60% of AMFI, skip the 1.5-persons-per-bedroom impute, or apply HERA Special columns to a 2010+ building.

## What's included

- `data/mtsp_limits.csv.gz` — 4,764 FY2026 50/60% MTSP + HERA Special columns
- `data/mtsp_incavg.csv.gz` — 4,764 income-averaging 20/30/40/70/80% columns
- `data/national_nonmetro.csv` — FY2026 national non-metro VLI (rural floor)
- `data/rent_rules.csv` / `data/setasides.csv` — 42(g) cites the desk actually uses
- `desk/quote.py` — `--county`, `--hera`, `--rural`, `--mix`, `--batch`, `--hera-areas`, `--floor-il`, `--ua-method`, `--ua-ladder`, `--s8-hap`, `--qct`, `--zcta`, `--boost`, `--lost-qct`
- `data/ua_methods.csv` — 10-rung 26 CFR 1.42-10 applicable-UA table
- `data/qct2026.csv.gz` / `qct2025.csv.gz` — HUD geocoded QCT lists (14,496 / 15,727 tracts)
- `data/dda_metro_zcta.csv` — 2,615 HUD 2026 metro Small DDA ZCTAs (DDA2026M.pdf)
- `data/dda_nonmetro_counties.csv` — 301 HUD 2026 nonmetro DDA counties (DDA2026NM.pdf)
- `examples/` — Autauga 2BR 60%; Barbour rural lift; Presidio HERA vs Regular; hold-harmless; UA ladder; QCT/DDA 30% boost
- `data/SOURCES.md` — HUD USER xlsx URLs + IRC / 1.42-10 / 42(d)(5)(B) cites

## Quick start

```bash
python3 desk/quote.py --watch
python3 desk/quote.py --county Autauga --state AL --br 2 --ami 60
python3 desk/quote.py --county Barbour --state AL --br 2 --ami 60 --rural --ua 80 --asking 1100
python3 desk/quote.py --county "Los Angeles" --state CA --br 1 --ami 60 --hera
python3 desk/quote.py --county Autauga --state AL --mix "2@30,6@60,2@80"
python3 desk/quote.py --batch data/sample_units.csv
python3 desk/quote.py --hera-areas 15
python3 desk/quote.py --rules
python3 desk/quote.py --ua-ladder
python3 desk/quote.py --county Autauga --state AL --br 2 --ami 60 --floor-il 54000
python3 desk/quote.py --county Autauga --state AL --br 2 --ami 60 --ua 80 --ua-method PHA-S8 --s8-hap 400 --asking 700
python3 desk/quote.py --qct 01001021000
python3 desk/quote.py --zcta 35213
python3 desk/quote.py --boost --county Autauga --state AL --qct 01001021000 --eligible-basis 10000000
python3 desk/quote.py --lost-qct AL
```

No API keys. No network after download.

## Price

$49 USD. Unlimited non-exclusive buyers; copies may be resold. Pay https://buy.stripe.com/5kQcN65pC7Z1aRQ9A9cIE08 then open a GitHub issue titled `CLAIM: LIHTC MTSP Rent Desk` with the receipt last-4. If checkout is down, star + watch and open the same CLAIM issue.

## License

MIT for code. HUD source tables remain public U.S. government data.

## Foundry

Shipped by Night Shift Foundry for Dakota (@Allspecs-yoda).
SKU: NSF-20260827-LIHTC-MTSP | Decision: list | Cycle: 2026-08-28 polish-qct-dda
