# Barbour County, AL — rural 42(i)(8) floor

```bash
python3 desk/quote.py --county Barbour --state AL --br 2 --ami 60
python3 desk/quote.py --county Barbour --state AL --br 2 --ami 60 --rural
```

Barbour is non-metro. Area 4-person 50% is $37,100, **below** the FY2026 national non-metro VLI $42,350. `--rural` takes the greater 50% then scales 60% as 120% of that VLI (HUD method). Confirm §520 rural status with the allocating agency before using the floor.
