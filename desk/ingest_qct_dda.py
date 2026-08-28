#!/usr/bin/env python3
"""Build offline 2026 QCT + DDA tables from HUD USER extracts.

Run from the repo root after dropping HUD files in /tmp/hud-qct:

  python3 desk/ingest_qct_dda.py

No network. Writes data/qct2026.csv.gz, data/qct2025.csv.gz,
data/dda_metro_zcta.csv, data/dda_nonmetro_counties.csv.
"""

from __future__ import annotations

import csv
import gzip
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SRC = Path("/tmp/hud-qct")

STATE_ABBR = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "Puerto Rico": "PR",
    "Guam": "GU",
    "American Samoa": "AS",
    "Northern Mariana Islands": "MP",
    "Virgin Islands": "VI",
}


def slim_qct(src: Path, year: int, dest: Path) -> int:
    n = 0
    with src.open(encoding="utf-8", newline="") as f, gzip.open(dest, "wt", encoding="utf-8", newline="") as out:
        r = csv.DictReader(f)
        w = csv.DictWriter(
            out,
            fieldnames=["year", "tract_fips", "stcnty", "statefp", "cbsa", "tract", "split"],
        )
        w.writeheader()
        for row in r:
            fips = re.sub(r"\D", "", row.get("fips") or "")
            if len(fips) == 10:
                fips = "0" + fips
            if len(fips) != 11:
                continue
            stcnty = re.sub(r"\D", "", row.get("stcnty") or fips[:5])
            if len(stcnty) == 4:
                stcnty = "0" + stcnty
            w.writerow(
                {
                    "year": year,
                    "tract_fips": fips,
                    "stcnty": stcnty[:5],
                    "statefp": (row.get("statefp") or fips[:2]).zfill(2),
                    "cbsa": (row.get("cbsa") or "").strip(),
                    "tract": (row.get("tract") or "").strip(),
                    "split": (row.get("splittr") or "0").strip() or "0",
                }
            )
            n += 1
    return n


def parse_metro_dda(text: str) -> list[dict]:
    rows: list[dict] = []
    state = ""
    area = ""
    skip = re.compile(
        r"^(2026 IRS|State\s+Metropolitan|\*Effective|\* indicates|Page \d+|Count =|$)"
    )
    continued = re.compile(r"^\(([A-Z]{2}) Continued\)\s+(.*)$")
    zcta_re = re.compile(r"\b(\d{5})\*?")
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if skip.search(line.strip()) or line.strip().startswith("Page "):
            continue
        if "SECTION 42" in line or "Metropolitan Area" in line and "DDA ZCTAs" in line:
            continue
        # continued ZCTA-only lines are indented and start with digits
        stripped = line.strip()
        if re.match(r"^\d{5}", stripped) and state and area:
            for m in zcta_re.finditer(stripped):
                token = m.group(0)
                rows.append(
                    {
                        "kind": "metro-zcta",
                        "year": 2026,
                        "stusps": STATE_ABBR.get(state, ""),
                        "state_name": state,
                        "area": area,
                        "zcta": m.group(1),
                        "split": "1" if token.endswith("*") else "0",
                    }
                )
            continue
        mcont = continued.match(stripped)
        if mcont:
            abbr = mcont.group(1)
            for name, code in STATE_ABBR.items():
                if code == abbr:
                    state = name
                    break
            rest = mcont.group(2)
        else:
            mstate = re.match(r"^([A-Z][A-Za-z .'-]+?)\s{2,}(\S.*)$", line)
            if mstate and mstate.group(1) in STATE_ABBR:
                state = mstate.group(1)
                rest = mstate.group(2)
            else:
                rest = stripped
        # rest: area name then zctas
        zctas = list(zcta_re.finditer(rest))
        if not zctas:
            continue
        area_part = rest[: zctas[0].start()].strip()
        if area_part:
            area = re.sub(r"\s+", " ", area_part)
        for m in zctas:
            token = m.group(0)
            rows.append(
                {
                    "kind": "metro-zcta",
                    "year": 2026,
                    "stusps": STATE_ABBR.get(state, ""),
                    "state_name": state,
                    "area": area,
                    "zcta": m.group(1),
                    "split": "1" if "*" in token else "0",
                }
            )
    return rows


def parse_nonmetro_dda(text: str) -> list[dict]:
    rows: list[dict] = []
    state = ""
    skip = re.compile(r"^(2026 IRS|State\s+Nonmetropolitan|\*Effective|Page \d+|Count =|$)")
    county_re = re.compile(
        r"(Northern Islands Municipality|Rota Municipality|Saipan Municipality|Tinian Municipality|"
        r"Eastern District|Western District|Manu'a District|Swains Island|"
        r"St\. Croix|St\. John|St\. Thomas|Guam|"
        r"[A-Z][A-Za-z.'’\- ]+?(?:County|Parish|Borough|Municipality|Census Area|City and Borough|Planning Region|District|Island|Municipio))"
    )
    for raw in text.splitlines():
        line = raw.rstrip().replace("á", "a").replace("í", "i").replace("é", "e").replace("ó", "o").replace("ú", "u").replace("ñ", "n").replace("ü", "u")
        if not line.strip() or skip.search(line.strip()) or "SECTION 42" in line:
            continue
        mstate = re.match(r"^([A-Z][A-Za-z .'-]+?)\s{2,}(\S.*)$", line)
        if mstate and mstate.group(1) in STATE_ABBR:
            state = mstate.group(1)
            rest = mstate.group(2)
        else:
            rest = line.strip()
        names = [m.group(1).strip() for m in county_re.finditer(rest)]
        if "Guam" in rest and state == "Guam":
            names = ["Guam"]
        for name in names:
            name = re.sub(r"\s+", " ", name).strip()
            rows.append(
                {
                    "kind": "nonmetro-county",
                    "year": 2026,
                    "stusps": STATE_ABBR.get(state, ""),
                    "state_name": state,
                    "county_name": name,
                }
            )
    # unique
    seen = set()
    out = []
    for r in rows:
        k = (r["stusps"], r["county_name"].lower())
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
    return out


def main() -> None:
    DATA.mkdir(exist_ok=True)
    n26 = slim_qct(SRC / "QCT2026.csv", 2026, DATA / "qct2026.csv.gz")
    n25 = slim_qct(SRC / "QCT2025.csv", 2025, DATA / "qct2025.csv.gz")
    metro = parse_metro_dda((SRC / "DDA2026M.txt").read_text(encoding="utf-8", errors="replace"))
    nm = parse_nonmetro_dda((SRC / "DDA2026NM.txt").read_text(encoding="utf-8", errors="replace"))

    with (DATA / "dda_metro_zcta.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["kind", "year", "stusps", "state_name", "area", "zcta", "split"])
        w.writeheader()
        # unique zcta+area
        seen = set()
        for r in metro:
            k = (r["zcta"], r["area"], r["stusps"])
            if k in seen:
                continue
            seen.add(k)
            w.writerow(r)
        metro_n = len(seen)

    with (DATA / "dda_nonmetro_counties.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["kind", "year", "stusps", "state_name", "county_name"])
        w.writeheader()
        for r in nm:
            w.writerow(r)

    print(f"qct2026 {n26}")
    print(f"qct2025 {n25}")
    print(f"metro zcta unique {metro_n} (HUD count 2615)")
    print(f"nonmetro counties {len(nm)} (HUD count 301)")
    print("zcta sample", metro[:3])
    print("nm sample", nm[:5])
    print("states metro", Counter(r["stusps"] for r in metro).most_common(8))


if __name__ == "__main__":
    main()
