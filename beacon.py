import argparse
import csv
import json
import math
from collections import defaultdict
from ipaddress import ip_address
from pathlib import Path
from statistics import median


def candidates(rows):
    series = defaultdict(set)
    for row in rows:
        src, dst = (str(ip_address(row[field])) for field in ("source", "destination"))
        port, stamp = int(row["port"]), float(row["epoch_seconds"])
        if not 1 <= port <= 65535 or not math.isfinite(stamp):
            raise ValueError("invalid port or timestamp")
        series[src, dst, port].add(stamp)
    result = []
    for (src, dst, port), stamps in series.items():
        if len(stamps) < 6:
            continue
        ordered = sorted(stamps)
        gaps = [b - a for a, b in zip(ordered, ordered[1:])]
        base = median(gaps)
        if base < 1:
            continue
        multiples = [max(1, round(gap / base)) for gap in gaps]
        matches = [m for m, gap in zip(multiples, gaps)
                   if m <= 3 and abs(gap - m * base) <= base * 0.1]
        score = len(matches) / len(gaps)
        if score >= 0.8 and matches.count(1) * 2 >= len(gaps):
            result.append(dict(source=src, destination=dst, port=port, period_seconds=base,
                               support=round(score, 3), observations=len(stamps), gaps=gaps))
    return sorted(result, key=lambda r: (-r["support"], -r["observations"], r["destination"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rank periodic outbound flow series")
    parser.add_argument("csv_file", type=Path)
    args = parser.parse_args()
    try:
        with args.csv_file.open(encoding="utf-8", newline="") as stream:
            print(json.dumps(candidates(csv.DictReader(stream)), indent=2))
    except (OSError, KeyError, ValueError) as exc:
        parser.exit(2, f"Invalid flow export: {exc}\n")
