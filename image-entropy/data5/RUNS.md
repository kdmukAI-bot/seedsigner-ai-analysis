# Fifth round, 2026-08-06: blank white wall

Two lit runs on one unit, captured on the **same verified build as rounds 2-4** (no new
image; see `PROVENANCE-round5-pi0.txt` in this directory, which duplicates the round-2/3
build record and states the attribution basis). The scene is the one people raise as a
worry: a blank white wall, nothing to look at. These runs measure whether a featureless
scene is a low-entropy scene.

| Runs | Unit | Board | Image | Provenance |
|---|---|---|---|---|
| `000053`, `000306` (`-6b66`) | `6b665e1fa1d5` | Pi Zero Rev 1.3 | `59ea2885` | `PROVENANCE-round5-pi0.txt` |

Both runs are one boot, minutes apart: elapsed-time names 53 s and 3 m 06 s, and the
free-space delta between the two capture.logs (13,950,976 bytes) matches one run's dump.
This boot is separate from the `data3`/`data4` sessions on this unit.

**Naming hazard, permanent:** `data5/000306-6b66` sits three seconds from
`data1/burst-19700101-000303` (same unit, pre-suffix naming era) and from
`data3/000303-6b66`. Never merge `dataN/` directories; cite every run with its `dataN/`
prefix.

## Conditions

A blank white wall: the most well-lit blank-wall area available to the operator, chosen
so the operator cast no shadow on it. No artificial lighting; natural overcast morning
light through a window. `000053` was captured handheld; `000306` with the device
stationary. AE settled differently between the two (digital gain 1.46 vs 2.07, AWB gains
differ), consistent with small framing and distance differences between a handheld and a
resting position.

## Results

Final image: MCV min-entropy (SP 800-90B 6.3.1, worst of all 45 pairs,
`../analyze_mcv.py`). Window: `../analyze_preview.py`, whole-window digest structure.
AE state from `ae_before_lock` in each capture.log. A 24-word seed needs 256 bits.

| Run | Capture | digital_gain | Window | Distinct | Worst live-live pair | Final MCV | vs 256 |
|---|---|---|---|---|---|---|---|
| `000053-6b66` | handheld | 1.46 | 50 | 43 | 157,848 | 1,397,876 | 5,460x |
| `000306-6b66` | stationary | 2.07 | 20 | **20 of 20** | 151,069 | 1,490,163 | 5,820x |

### A featureless scene is not a degenerate scene

Both finals land within 10% of the same unit's detail-rich lit baselines
(`data1/burst-19700101-000303` bookshelf: 1,505,982; `data3/000630-6b66` lit control:
1,544,107). Scene structure contributes almost nothing to these figures; the entropy is
per-pixel sensor noise, and a uniformly lit field exercises it as fully as a cluttered
one. Between any two distinct preview frames, 37-75% of bytes changed. The frames are
full-color images (all three channels populated in every dumped frame), not the
near-binary green quantization plane the dark runs produce.

### The stationary run is the maximally boring capture

`000306` has no scene detail, no camera motion, and no artificial light, and still
returned **20 of 20 distinct frames** with a worst pair of 151,069 bits (590x the
requirement from a single pair). Hand shake is not what the entropy rests on; neither is
scene content. What both runs have that the dark runs lack is illumination.

### AE state: nowhere near the dark rail

The dark-scene failure mode rides the gain rail (digital gain 3.25/3.625, unanimous
across all recorded dark sessions). The white wall settled at 1.46 and 2.07 with analog
gain 1.19-2.06. As far as the pipeline is concerned this is an ordinary lit scene; the
degenerate axis is illumination, not featurelessness.

### Cached doubles on the single-core board, again

`000053`'s seven repeats (43 distinct of 50) are all adjacent-slot digest doubles. The
four whose content is in the dump (slots 9/10, 15/16, 17/18, 46/47) are byte-identical
live frames: the cached-buffer re-return already demonstrated lit (`data3/000630`, 46 of
50) and dark (`data4/000523`) on single-core boards. Loop rate 11.20 fps against 9.59 fps
delivery; the other three doubles sit in the undumped mid-window, distinct-digest
structure known from the log.

### A fast-capture datapoint

`000306` was clicked 1.868 s after stream start, so only 20 preview frames existed to
chain (the window holds up to 50). The minimum-dwell case still delivered a fully live,
fully distinct window; at ~151k bits per pair, dwell time is not where the margin comes
from in a lit scene.

## Combined accounting

Same conventions as `data3/RUNS.md`: dumped distinct live frames x that run's worst
within-run live-live MCV; cached duplicates at zero; CPU serial at zero; `time.time()`
(~25-30 bits, estimated not measured) excluded.

| Run | Preview (measured) | Final | Total | Clears 256? |
|---|---|---|---|---|
| `000053-6b66` | 29 dumped x 157,848 | 1,397,876 | ~6.0 million | yes, overwhelmingly |
| `000306-6b66` | 20 x 151,069 = 3,021,380 | 1,490,163 | ~4.5 million | yes, overwhelmingly |

Standing caveats, unchanged: MCV over-estimates the floor on non-IID data; multiplying a
pairwise figure by frame count overstates; summing layers assumes an independence the
coupling measurements show is imperfect. In these runs the margin is four orders of
magnitude, so the caveats change no conclusion.

## Retained

Both runs, in full. No selection criterion was applied.

## Scope

One unit, one wall, one morning, n=2. What these runs establish: the "blank wall" worry
conflates featurelessness with darkness. A lit featureless scene cleared the requirement
by four orders of magnitude on the weakest single-core unit in the fleet, with or without
hand motion, and behaved like the lit controls on every measured axis (distinct-frame
count, per-pair novelty, AE state, final-image margin). The case the warnings cover
remains the unlit one.
