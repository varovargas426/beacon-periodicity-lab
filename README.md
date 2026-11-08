# Beacon Periodicity Lab

Rank outbound network flows by timing regularity and inspect how a missed observation affects a possible beacon.

## Reproduce the case

Requires Python 3.11+. All examples use synthetic data and run locally with the standard library. Run from the repository root.

```sh
python beacon.py examples/flows.csv
```

The lab contains three destinations: one repeats around 60 seconds with a missing interval, one has irregular traffic, and one has too few observations. Only the first enters the candidate list. Its gap list makes the two-minute pause visible to the analyst.

## Design and limits

Group by source, destination and destination port, deduplicate timestamps, and estimate the period using the median gap. A gap supports the estimate if it lies within 10% of one of its first three multiples. Candidates require at least six observations, 80% supporting gaps and at least half the gaps near the base period. This heuristic is sensitive to duty-cycle changes and NAT. Scheduled backups and health checks are expected false positives. The CLI ingests a bounded CSV export in memory and makes no network requests.

## Verification

```sh
python -m unittest discover -s tests -v
```

Tests distinguish a missed pulse from irregular traffic, enforce the evidence threshold, and check that repeated rows do not manufacture a periodic signal.
