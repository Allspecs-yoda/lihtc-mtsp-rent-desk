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

- [26 U.S.C. § 42(g)(2)](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section42) — rent-restricted = gross rent ≤ 30% of imputed income limitation; 0 BR → 1 person; ≥1 BR → 1.5 persons per bedroom; hold-harmless vs first year in the project.
- [26 U.S.C. § 42(g)(1)](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section42) — 20-50 / 40-60 / income averaging.
- [26 U.S.C. § 42(i)(8)](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section42) — rural: greater of area median or national non-metropolitan median.
- HUD USER: 60% MTSP = 120% of the 50% (very-low) limit. Do **not** take 60% of median family income directly (too many HUD exceptions).
- HERA Special columns are **only** for buildings placed in service in 2007 or 2008.

## What this desk does **not** do

- Does not replace the allocating HFA, IRS Form 8609, or a BIN hold-harmless schedule.
- Does not apply state overlay rents (e.g. California HCD, NY HCR) or HOME 92.252 High/Low HOME (those are a different HUD file).
- Does not fetch live HUD USER. If HUD revises the xlsx, replace the gz files.
