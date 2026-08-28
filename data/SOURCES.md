# Sources

All figures in this pack are copied or derived from public HUD USER FY2026 MTSP files. No invented AMIs. No network after you unzip the repo.

## Primary tables

| file | source | retrieved |
| --- | --- | --- |
| `mtsp_limits.csv.gz` | [FY 2026 MTSP Income Limits data in MS Excel](https://www.huduser.gov/portal/datasets/mtsp/mtsp26/MTSP-Data-FY26.xlsx) linked from [HUD USER MTSP](https://www.huduser.gov/portal/datasets/mtsp.html) | 2026-08-27 |
| `mtsp_incavg.csv.gz` | [FY 2026 MTSP Income Averaging data in MS Excel](https://www.huduser.gov/portal/datasets/mtsp/mtsp26/MTSP-IncAvg-Data-FY26.xlsx) (HUD note: updated 2026-05-18 to remove rounding from non-50% income limits) | 2026-08-27 |
| `national_nonmetro.csv` | [FY2026 National Non-Metro Very Low-Income Limits](https://www.huduser.gov/portal/datasets/il/il26/FY2026-National-Non-Metro-Very-Low-Income-Limits.xlsx) | 2026-08-27 |

Effective date on the HUD MTSP page: **May 1, 2026**.

Row counts in this pack: **4,764** county/town rows in each MTSP file (header excluded). Unique `hud_area_code`: **2,635**. `HERA_Lim_type26=Special`: **2,277** rows / **1,439** areas.

## Statute / rule cites (rent math)

- [26 U.S.C. § 42(g)(2)](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section42) — rent-restricted = gross rent ≤ 30% of imputed income limitation; 0 BR → 1 person; ≥1 BR → 1.5 persons per bedroom; hold-harmless vs first year in the project. `--floor-il` takes max(FY2026, prior imputed IL).
- [26 U.S.C. § 42(g)(1)](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section42) — 20-50 / 40-60 / income averaging.
- [26 U.S.C. § 42(i)(8)](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section42) — rural: greater of area median or national non-metropolitan median.
- [26 CFR § 1.42-10](https://www.law.cornell.edu/cfr/text/26/1.42-10) — applicable UA ladder (RHS → RHS-tenant → HUD-regulated → PHA-S8 → PHA default / company / agency / HUSM / energy). Telephone/cable/internet never UA. New UA hits rents due 90 days after the change ((c)(1)); annual owner review ((c)(2)). Submetering ((e)): admin fee ≤ $5/mo (or state cap) is not gross rent. Section 8 HAP is excluded from gross rent (42(g)(2)(B)(i)).
- [26 U.S.C. § 42(d)(5)(B)](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section42) — buildings in a QCT (ii) or DDA (iii) may increase eligible basis (new construction / rehab, **not land**) by 30%. This is **not** a 42(g)(2) rent increase. HUD designates annually.

## QCT / DDA tables (2026 designations, effective 2026-01-01)

| file | source | retrieved | rows |
| --- | --- | --- | --- |
| `qct2026.csv.gz` | [2026 Qualified Census Tracts — Geocoded CSV](https://www.huduser.gov/portal/datasets/qct/QCT2026CSV.zip) (`QCT2026.csv`) | 2026-08-28 | 14,496 tracts |
| `qct2025.csv.gz` | [2025 Qualified Census Tracts — Geocoded CSV](https://www.huduser.gov/portal/datasets/qct/QCT2025CSV.zip) (`QCT2025.csv`) | 2026-08-28 | 15,727 tracts (2,464 lost / 1,233 gained vs 2026) |
| `dda_metro_zcta.csv` | [2026 Metropolitan Difficult Development Areas (DDA2026M.pdf)](https://www.huduser.gov/portal/datasets/qct/DDA2026M.pdf) — HUD footer **Count = 2,615 metropolitan ZCTAs** | 2026-08-28 | 2,615 ZCTA rows (2,560 unique; split ZCTAs repeat across HMFAs) |
| `dda_nonmetro_counties.csv` | [2026 Non-metropolitan Difficult Development Areas (DDA2026NM.pdf)](https://www.huduser.gov/portal/datasets/qct/DDA2026NM.pdf) — HUD footer **Count = 301 nonmetropolitan DDAs** | 2026-08-28 | 301 counties / equivalents |

Designation notice: HUD, *Statutorily Mandated Designation of Difficult Development Areas and Qualified Census Tracts for 2026*, **90 FR 46904** (Sept. 30, 2025) ([2025-19007](https://www.federalregister.gov/documents/2025/09/30/2025-19007/statutorily-mandated-designation-of-difficult-development-areas-and-qualified-census-tracts-for-2026)). Rebuild CSVs with `python3 desk/ingest_qct_dda.py` after dropping the HUD extracts in `/tmp/hud-qct`. Metro Small DDAs use **2020 ZCTAs**, not live USPS ZIP — confirm splits on the [HUD SADDA locator](https://www.huduser.gov/portal/sadda/sadda_qct.html).
- HUD USER: 60% MTSP = 120% of the 50% (very-low) limit. Do **not** take 60% of median family income directly (too many HUD exceptions).
- HERA Special columns are **only** for buildings placed in service in 2007 or 2008.
- 45-day implement: HUD MTSP effective **2026-05-01**; LIHTC properties must use the new limits by **2026-06-15** (industry/HFA practice from the HUD release).

## What this desk does **not** do

- Does not replace the allocating HFA, IRS Form 8609, or a BIN hold-harmless schedule.
- Does not apply state overlay rents (e.g. California HCD, NY HCR) or HOME 92.252 High/Low HOME (those are a different HUD file).
- Does not fetch live HUD USER. If HUD revises the xlsx, replace the gz files.
- Does not decide HFA basis-boost awards, 42(m) allocations, or 2025-QCT grandfather from a binding-commitment file. `--boost` is a table lookup.
