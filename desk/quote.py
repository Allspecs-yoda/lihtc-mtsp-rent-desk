#!/usr/bin/env python3
"""LIHTC MTSP Rent Desk — offline FY2026 HUD MTSP quotes.

No network. No API keys. Planning only — not an HFA / 8609 determination.

  python3 desk/quote.py --watch
  python3 desk/quote.py --county "Los Angeles" --state CA --br 1 --ami 60
  python3 desk/quote.py --county Autauga --state AL --br 2 --ami 60 --asking 1180
  python3 desk/quote.py --county Autauga --state AL --br 2 --ami 60 --hera
  python3 desk/quote.py --county Barbour --state AL --br 2 --ami 60 --rural --ua 80
  python3 desk/quote.py --county Autauga --state AL --mix "2@30,6@60,2@80"
  python3 desk/quote.py --batch data/sample_units.csv
  python3 desk/quote.py --list CA
  python3 desk/quote.py --hera-areas 15
  python3 desk/quote.py --rules
"""

from __future__ import annotations

import argparse
import csv
import gzip
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

AMIS = (20, 30, 40, 50, 60, 70, 80)
PERSONS = (1, 2, 3, 4, 5, 6, 7, 8)

# IRC 42(g)(2)(C): 0 BR → 1 person; n BR → 1.5 n persons.
# Fractional persons use the midpoint of the two HUD household-size columns.
BR_PERSONS = {0: 1.0, 1: 1.5, 2: 3.0, 3: 4.5, 4: 6.0, 5: 7.5, 6: 9.0}


def money(n: float) -> str:
    return f"${int(round(n)):,}"


def gz_or_plain(name: str) -> Path:
    gz = DATA / f"{name}.gz"
    raw = DATA / name
    if gz.exists():
        return gz
    if raw.exists():
        return raw
    raise SystemExit(f"missing data/{name}(.gz)")


def open_table(name: str):
    path = gz_or_plain(name)
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8", newline="")
    return path.open(encoding="utf-8", newline="")


def load_csv(name: str) -> list[dict]:
    with open_table(name) as f:
        return list(csv.DictReader(f))


def load_plain(name: str) -> list[dict]:
    path = DATA / name
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


_LIMITS: list[dict] | None = None
_IA: list[dict] | None = None
_NNM: dict | None = None


def limits() -> list[dict]:
    global _LIMITS
    if _LIMITS is None:
        _LIMITS = load_csv("mtsp_limits.csv")
    return _LIMITS


def incavg() -> list[dict]:
    global _IA
    if _IA is None:
        _IA = load_csv("mtsp_incavg.csv")
    return _IA


def nnm() -> dict:
    global _NNM
    if _NNM is None:
        rows = load_plain("national_nonmetro.csv")
        _NNM = rows[0]
    return _NNM


def ia_by_fips() -> dict[str, dict]:
    return {r["fips"]: r for r in incavg()}


def parse_int(s) -> int:
    t = str(s).strip().replace(",", "").replace("$", "")
    if t in ("", "-", "None"):
        return 0
    return int(float(t))


def col_50(row: dict, p: int, hera: bool) -> str:
    if hera:
        return f"Lim50_HERA_26p{p}"
    return f"lim50_26p{p}"


def col_60(row: dict, p: int, hera: bool) -> str:
    if hera:
        return f"Lim60_HERA_26p{p}"
    # published file mixes Lim60_26pN
    k = f"Lim60_26p{p}"
    if k in row:
        return k
    return f"lim60_26p{p}"


def col_ia(ami: int, p: int) -> str:
    if ami == 50:
        return f"lim50_26p{p}"
    if ami == 60:
        return f"Lim60_26p{p}"
    return f"Lim{ami}_IA_26p{p}"


def vli_person(row: dict, p: int, hera: bool) -> int:
    if p <= 8:
        return parse_int(row[col_50(row, p, hera)])
    # HUD extra-person: +8% of 4-person VLI per person over 8
    base8 = parse_int(row[col_50(row, 8, hera)])
    four = parse_int(row[col_50(row, 4, hera)])
    extra = p - 8
    return int(round(base8 + 0.08 * four * extra))


def nnm_vli(p: int) -> int:
    row = nnm()
    if p <= 8:
        return parse_int(row[f"vli_{p}"])
    four = parse_int(row["vli_4"])
    base8 = parse_int(row["vli_8"])
    return int(round(base8 + 0.08 * four * (p - 8)))


def floor_vli(row: dict, p: int, hera: bool, rural: bool) -> int:
    area = vli_person(row, p, hera)
    if not rural:
        return area
    return max(area, nnm_vli(p))


def hud_pct_of_vli(vli: int, ami: int) -> int:
    """HUD method: N% = (N/50) × 50% VLI, nearest dollar."""
    if ami == 50:
        return vli
    return int(round(vli * (ami / 50.0)))


def published_or_scaled(row: dict, ia: dict | None, p: int, ami: int, hera: bool, rural: bool) -> tuple[int, str]:
    """Return (annual IL, source tag). Rural / extra-person always scale from floored 50%."""
    if p > 8 or rural:
        return hud_pct_of_vli(floor_vli(row, p, hera, rural), ami), "scale-from-50"
    if hera and ami in (50, 60):
        key = col_50(row, p, True) if ami == 50 else col_60(row, p, True)
        val = parse_int(row.get(key, 0))
        if val:
            return val, "hera-special"
    if ami in (50, 60):
        key = col_50(row, p, False) if ami == 50 else col_60(row, p, False)
        return parse_int(row[key]), "mtsp-published"
    if ia is not None:
        key = col_ia(ami, p)
        if key in ia and str(ia[key]).strip():
            return parse_int(ia[key]), "incavg-published"
    return hud_pct_of_vli(floor_vli(row, p, hera, rural), ami), "scale-from-50"


def il_for_persons(row: dict, ia: dict | None, persons: float, ami: int, hera: bool, rural: bool) -> tuple[int, str]:
    lo = int(persons)
    hi = lo if persons == lo else lo + 1
    a, sa = published_or_scaled(row, ia, lo, ami, hera, rural)
    if hi == lo:
        return a, sa
    b, sb = published_or_scaled(row, ia, hi, ami, hera, rural)
    # midpoint, nearest dollar (HUD 4.5-person style)
    return int(round((a + b) / 2.0)), f"midpoint {lo}/{hi} ({sa})"


def monthly_max(annual_il: int) -> int:
    # Industry / HFA convention: truncate 30% of annual / 12 to whole dollars.
    return int(annual_il * 0.30 / 12.0)


def find_counties(needle: str, state: str | None) -> list[dict]:
    n = needle.strip().lower()
    st = state.upper() if state else None
    hits = []
    for r in limits():
        if st and r["stusps"] != st:
            continue
        county = (r.get("County_Name") or "").lower()
        town = (r.get("county_town_name") or "").lower()
        area = (r.get("hud_area_name") or "").lower()
        if n == county or n in county or n == town or n in town or n in area:
            hits.append(r)
    if not hits:
        raise SystemExit(f"No county matched {needle!r}" + (f" in {st}" if st else ""))
    return hits


def pick_county(hits: list[dict], needle: str) -> dict:
    n = needle.strip().lower()
    exact = [
        h
        for h in hits
        if (h.get("County_Name") or "").lower() in (n, n + " county")
        or (h.get("county_town_name") or "").lower() in (n, n + " county", n + " town", n + " town city", n + " city")
    ]
    if len(exact) == 1:
        return exact[0]
    if len(hits) == 1:
        return hits[0]
    codes = {h["hud_area_code"] for h in hits}
    if len(codes) == 1:
        return exact[0] if exact else hits[0]
    names = ", ".join(
        f"{h.get('county_town_name')} {h['stusps']} ({h['hud_area_code']})" for h in hits[:12]
    )
    raise SystemExit(f"Ambiguous. Matches: {names}. Pass --state or a tighter --county.")


def hera_ok(row: dict, hera: bool) -> None:
    if not hera:
        return
    t = (row.get("HERA_Lim_type26") or "").strip()
    if t.lower() != "special":
        print(
            f"note: {row.get('hud_area_name')} HERA_Lim_type26={t or 'blank'} — HERA Special columns are empty/equal; --hera is a no-op here.",
            file=sys.stderr,
        )


def quote_row(row: dict, br: int, ami: int, hera: bool, rural: bool, ua: int, asking: int | None) -> dict:
    if br not in BR_PERSONS:
        raise SystemExit("--br must be 0–6")
    if ami not in AMIS:
        raise SystemExit("--ami must be 20/30/40/50/60/70/80")
    hera_ok(row, hera)
    ia = ia_by_fips().get(row["fips"])
    persons = BR_PERSONS[br]
    annual, src = il_for_persons(row, ia, persons, ami, hera, rural)
    mx = monthly_max(annual)
    tenant_cap = mx - ua
    out = {
        "fips": row["fips"],
        "stusps": row["stusps"],
        "county_town_name": row.get("county_town_name"),
        "hud_area_code": row["hud_area_code"],
        "hud_area_name": row["hud_area_name"],
        "metro": row["metro"],
        "median2026": parse_int(row.get("median2026", 0)),
        "hera_type": row.get("HERA_Lim_type26"),
        "br": br,
        "imputed_persons": persons,
        "ami": ami,
        "hera": int(hera),
        "rural": int(rural),
        "annual_il": annual,
        "il_source": src,
        "monthly_max_gross": mx,
        "ua": ua,
        "tenant_rent_cap": tenant_cap,
        "asking": asking if asking is not None else "",
    }
    if asking is not None:
        gross = asking + ua
        out["asking_gross"] = gross
        out["over_max"] = int(gross > mx)
        out["headroom"] = mx - gross
    return out


def print_quote(q: dict) -> None:
    print(f"{q['county_town_name']}, {q['stusps']} — {q['hud_area_name']}")
    print(f"  area {q['hud_area_code']}  metro={q['metro']}  AMFI {money(q['median2026'])}  HERA={q['hera_type']}")
    print(
        f"  {q['br']} BR  imputed {q['imputed_persons']}p  {q['ami']}% AMI"
        + ("  HERA-special" if q["hera"] else "")
        + ("  rural-floor" if q["rural"] else "")
    )
    print(f"  annual imputed IL {money(q['annual_il'])}  ({q['il_source']})")
    print(f"  42(g)(2) monthly gross max {money(q['monthly_max_gross'])}  (30% / 12, truncated)")
    if q["ua"]:
        print(f"  minus UA {money(q['ua'])} → tenant rent cap {money(q['tenant_rent_cap'])}")
    if q["asking"] != "":
        flag = "OVER" if q["over_max"] else "ok"
        print(
            f"  asking tenant {money(q['asking'])} + UA {money(q['ua'])} = gross {money(q['asking_gross'])}  [{flag}]  headroom {money(q['headroom'])}"
        )


def cmd_watch() -> None:
    rows = limits()
    special = sum(1 for r in rows if (r.get("HERA_Lim_type26") or "").lower() == "special")
    areas = {r["hud_area_code"] for r in rows}
    nn = nnm()
    print("LIHTC MTSP Rent Desk — FY2026")
    print(f"  rows {len(rows):,}  unique HUD areas {len(areas):,}  HERA Special rows {special:,}")
    print(f"  effective 2026-05-01  national non-metro 4p VLI {money(parse_int(nn['vli_4']))}")
    print("  rent-restricted = 30% of IRC 42(g)(2)(C) imputed IL / 12")
    print("  HERA Special is 2007/2008 PIS only. Rural floor is IRC 42(i)(8).")
    print("  not an HFA determination")


def cmd_rules() -> None:
    for r in load_plain("rent_rules.csv"):
        print(f"{r['rule_id']}: {r['cite']}")
        print(f"  {r['what']}")
        print(f"  desk: {r['how_this_desk']}")
        print()


def cmd_list(state: str) -> None:
    st = state.upper()
    seen = []
    codes = set()
    for r in limits():
        if r["stusps"] != st:
            continue
        code = r["hud_area_code"]
        if code in codes:
            continue
        codes.add(code)
        seen.append(r)
    print(f"{st}: {len(seen)} HUD areas")
    for r in seen:
        four50 = parse_int(r["lim50_26p4"])
        print(
            f"  {r['hud_area_code']:22}  4p50 {money(four50):>8}  HERA={r.get('HERA_Lim_type26')}  {r['hud_area_name']}"
        )


def cmd_hera_areas(n: int) -> None:
    seen = {}
    for r in limits():
        if (r.get("HERA_Lim_type26") or "").lower() != "special":
            continue
        code = r["hud_area_code"]
        if code in seen:
            continue
        a = parse_int(r["lim50_26p4"])
        h = parse_int(r.get("Lim50_HERA_26p4") or 0)
        seen[code] = (h - a, r, a, h)
    ranked = sorted(seen.values(), key=lambda t: t[0], reverse=True)
    print(f"HERA Special areas by 4-person 50% lift vs Regular (top {n} of {len(ranked)})")
    for lift, r, a, h in ranked[:n]:
        print(f"  {money(lift):>8}  {r['stusps']}  {r['hud_area_name']}  regular {money(a)}  hera {money(h)}")


def parse_mix(spec: str) -> list[tuple[int, int]]:
    out = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "@" not in part:
            raise SystemExit(f"bad mix token {part!r}; use N@AMI")
        n_s, ami_s = part.split("@", 1)
        n, ami = int(n_s), int(ami_s)
        if ami not in AMIS:
            raise SystemExit(f"mix AMI {ami} not in {AMIS}")
        if n <= 0:
            raise SystemExit("mix counts must be positive")
        out.append((n, ami))
    if not out:
        raise SystemExit("empty --mix")
    return out


def cmd_mix(row: dict, spec: str, hera: bool, rural: bool) -> None:
    units = parse_mix(spec)
    total = sum(n for n, _ in units)
    weighted = 0.0
    print(f"{row.get('county_town_name')}, {row['stusps']} — {row['hud_area_name']}")
    print(f"  income averaging mix  total units {total}")
    over80 = False
    for n, ami in units:
        if ami > 80:
            over80 = True
        weighted += n * ami
        print(f"  {n:3} units @ {ami}%")
    avg = weighted / total
    ok = avg <= 60 + 1e-9 and not over80
    print(f"  unit-weighted average {avg:.2f}%   cap 60%   [{'PASS' if ok else 'FAIL'}]")
    if over80:
        print("  FAIL: a designated unit exceeds 80% (IRC 42(g)(1)(C))")
    print("  2 BR monthly gross max at each designated AMI:")
    for n, ami in units:
        q = quote_row(row, 2, ami, hera, rural, 0, None)
        print(f"    {ami}% → {money(q['monthly_max_gross'])}/mo gross  IL {money(q['annual_il'])}")


def cmd_batch(path: Path) -> None:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    w = csv.DictWriter(
        sys.stdout,
        fieldnames=[
            "label",
            "county_town_name",
            "stusps",
            "hud_area_code",
            "br",
            "ami",
            "annual_il",
            "monthly_max_gross",
            "ua",
            "tenant_rent_cap",
            "asking",
            "over_max",
            "hera_type",
            "il_source",
        ],
    )
    w.writeheader()
    for s in rows:
        hits = find_counties(s["county"], s.get("state") or None)
        row = pick_county(hits, s["county"])
        q = quote_row(
            row,
            int(s["br"]),
            int(s["ami"]),
            bool(int(s.get("hera") or 0)),
            bool(int(s.get("rural") or 0)),
            parse_int(s.get("ua") or 0),
            parse_int(s["asking"]) if str(s.get("asking") or "").strip() else None,
        )
        w.writerow(
            {
                "label": s.get("label", ""),
                "county_town_name": q["county_town_name"],
                "stusps": q["stusps"],
                "hud_area_code": q["hud_area_code"],
                "br": q["br"],
                "ami": q["ami"],
                "annual_il": q["annual_il"],
                "monthly_max_gross": q["monthly_max_gross"],
                "ua": q["ua"],
                "tenant_rent_cap": q["tenant_rent_cap"],
                "asking": q["asking"],
                "over_max": q.get("over_max", ""),
                "hera_type": q["hera_type"],
                "il_source": q["il_source"],
            }
        )


def main() -> None:
    p = argparse.ArgumentParser(description="FY2026 LIHTC MTSP rent desk")
    p.add_argument("--watch", action="store_true")
    p.add_argument("--rules", action="store_true")
    p.add_argument("--list", metavar="ST", help="list HUD areas in a state")
    p.add_argument("--hera-areas", type=int, nargs="?", const=15)
    p.add_argument("--county")
    p.add_argument("--state")
    p.add_argument("--br", type=int, default=2)
    p.add_argument("--ami", type=int, default=60)
    p.add_argument("--hera", action="store_true")
    p.add_argument("--rural", action="store_true")
    p.add_argument("--ua", type=int, default=0)
    p.add_argument("--asking", type=int)
    p.add_argument("--mix", help='income-averaging mix, e.g. "2@30,6@60,2@80"')
    p.add_argument("--batch", type=Path)
    args = p.parse_args()

    if args.watch:
        cmd_watch()
        return
    if args.rules:
        cmd_rules()
        return
    if args.list:
        cmd_list(args.list)
        return
    if args.hera_areas is not None:
        cmd_hera_areas(args.hera_areas)
        return
    if args.batch:
        cmd_batch(args.batch)
        return
    if not args.county:
        p.print_help()
        raise SystemExit(2)
    row = pick_county(find_counties(args.county, args.state), args.county)
    if args.mix:
        cmd_mix(row, args.mix, args.hera, args.rural)
        return
    q = quote_row(row, args.br, args.ami, args.hera, args.rural, args.ua, args.asking)
    print_quote(q)


if __name__ == "__main__":
    main()
