# Lit bookshelf series -- one run per unit, all four hardware units

The retained lit-scene baseline: the same well-lit bookshelf scene captured once on each
physical unit in the fleet. These are the provenance-clean backing for every lit-scene
claim and exhibit; the older `data/burst-lit*` series that previously served that role are
quarantined (no provenance records, pre-gate build -- see the quarantine README).

## Build

Captured during the 2026-08-05 dark-floor campaign (`data2`), on its instrumented build:
app `0.8.7` @ `e0a80d4b`, OS `v0.8.7` @ `d1385939` (both upstream-verified), patch
`f1c059df`. Per-run provenance files did not yet exist in that era; the attribution basis
is (1) same-campaign import and (2) `data2/RUNS.md` documents three of these four runs
(`000029`, `000111`, `000303`) as byte-identical copies deleted from `data2` as
duplicates of the copies here.

## Runs

MCV = SP 800-90B 6.3.1 most-common-value min-entropy, worst of all 45 pairs, via
`../analyze_mcv.py`. A 24-word seed needs 256 bits.

| Run | unit_id | Board | Still | MCV (all pairs) | vs 256 |
|---|---|---|---|---|---|
| `burst-19700101-000025` | `934f1769250d` | Pi Zero 2 W Rev 1.0 | 480x480 | 1,748,713 | 6,830x |
| `burst-19700101-000029` | `074c518d70fb` | Pi Zero W Rev 1.1 (bare) | 480x480 | 1,581,192 | 6,176x |
| `burst-19700101-000111` | `a92ac791f26b` | Pi Zero W Rev 1.1 + Plus | 640x640 | 3,131,353 | 12,231x |
| `burst-19700101-000303` | `6b665e1fa1d5` | Pi Zero Rev 1.3 | 480x480 | 1,505,982 | 5,882x |

**Geometry caveat:** the Plus still is 640x640 (1,228,800 values), 1.78x the 480x480
runs' 691,200. Absolute bit counts scale with value count, so the Plus figure is not
"2x better hardware" -- normalized per-value it sits in line with the other three
(~1.76M equivalent). Compare across resolutions per-value, never by raw total.

## Scope

Final image only. These runs chained preview frames (as every capture does) but the
preview-measurement instrumentation did not exist until patch `78dc66ea`; lit-scene
preview behavior was measured later, in `data3` (`000630-6b66`: 46 of 50 distinct) and
`data3`/`data4` (`000322-934f`: 50 of 50).

What these four runs establish: an ordinary lit scene clears the requirement by three to
four orders of magnitude on every hardware unit in the fleet, at both still geometries.
The retired published figure for this claim (1,483,426, from quarantined
`data/burst-lit2` under an older estimator version) is superseded by this table.
