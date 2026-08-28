# IRC 42(d)(5)(B) 30% eligible-basis boost

```bash
python3 desk/quote.py --qct 01001021000
python3 desk/quote.py --zcta 35213
python3 desk/quote.py --boost --county Autauga --state AL --qct 01001021000 --eligible-basis 10000000
python3 desk/quote.py --county Chambers --state AL --br 2 --ami 60 --boost --eligible-basis 5000000
python3 desk/quote.py --lost-qct AL
```

Autauga tract `01001021000` is on HUD’s **2026** QCT list (not 2025). Chambers County, AL is a **2026 nonmetro DDA**. ZCTA `35213` is a **2026 metro Small DDA** (Birmingham-Hoover, AL HMFA). A $10,000,000 eligible basis (user figure, land excluded) scales to $13,000,000 when the table hits; **monthly 42(g)(2) rent does not change**.

Tract `01091973001` is 2025-only (`--lost-qct`). Grandfather needs a binding commitment dated while the 2025 designation applied (HUD notice 90 FR 46904, Sept 30 2025) — this desk does not invent that fact. Split ZCTAs must be confirmed on the HUD SADDA locator; ZIP ≠ ZCTA.
