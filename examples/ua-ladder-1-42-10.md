# 26 CFR 1.42-10 UA ladder

```bash
python3 desk/quote.py --ua-ladder
python3 desk/quote.py --county Autauga --state AL --br 2 --ami 60 --ua 80 --ua-method PHA-DEFAULT --asking 1100
python3 desk/quote.py --county Autauga --state AL --br 2 --ami 60 --ua 80 --ua-method PHA-S8 --s8-hap 400 --asking 700
```

First matching rung wins (RHS building → any RHS tenant → HUD-regulated → PHA for S8 tenants → PHA default / company / agency / HUSM / energy). Telephone, cable, and Internet are never UA. A new UA applies to rents **due 90 days** after the change. HAP is excluded from gross rent; tenant rent + UA is what 42(g)(2) tests.
