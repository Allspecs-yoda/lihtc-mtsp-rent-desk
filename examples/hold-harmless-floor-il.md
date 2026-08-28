# Hold-harmless — Autauga 2 BR 60% with a prior imputed IL

IRC 42(g)(2)(A) 2d sentence: the imputed income limitation for a unit is never less than the limitation for the earliest period the building (which contains the unit) was in the qualified project.

```bash
python3 desk/quote.py --county Autauga --state AL --br 2 --ami 60
python3 desk/quote.py --county Autauga --state AL --br 2 --ami 60 --floor-il 54000
```

If FY2026 imputed IL is below `--floor-il`, the desk uses the floor and flags HOLD-HARMLESS. This is a planning quote, not a BIN / Form 8609 determination. Confirm the prior-year figure against the allocating HFA schedule.
