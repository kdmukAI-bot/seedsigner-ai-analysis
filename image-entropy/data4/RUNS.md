# Fourth round, 2026-08-06: replication, and a third geometry

Nine dark runs across three boards, captured on the **same verified builds as rounds 2-3**
(no new images; see the three `PROVENANCE-round4-*.txt` files in this directory, which
duplicate the round-2/3 build records and state the attribution basis). First-ever preview
measurement on the Plus-display configuration; first replications of the preview-zero state
across a reboot.

| Runs | Unit | Board | Image | Provenance |
|---|---|---|---|---|
| `000025`, `000117`, `000212` (`-934f`) | `934f1769250d` | Pi Zero 2 W | `ac52e24e` | `PROVENANCE-round4-pi02w.txt` |
| `000123`, `000236`, `000412`, `000523` (`-6b66`) | `6b665e1fa1d5` | Pi Zero Rev 1.3 | `59ea2885` | `PROVENANCE-round4-pi0.txt` |
| `000038`, `000450` (`-a92a`) | `a92ac791f26b` | Pi Zero W + Plus display | `59ea2885` | `PROVENANCE-round4-plus.txt` |

**Naming hazard, permanent:** `000025-934f` and `000117-934f` also exist in `data3/` --
same unit, different boots, identical elapsed-time names. The on-device unit suffix
prevents cross-unit collisions only. Never merge `dataN/` directories; cite every run with
its `dataN/` prefix (near-misses recur: this round's `000412` vs data3's `000408`).

## Conditions

Dark captures at the **same shadowed desk position as the `data3` dark runs** (operator,
recorded 2026-08-06), face-down. Two runs fall in the
light-present band by the `data2` discriminator (share of first-frame values >= 4) and are
flagged in every table below; the other seven are properly dark (0.0009-0.0039%).

| Run | pct >= 4 | Band |
|---|---|---|
| `000038-a92a` | 0.1646% | light present (Plus internal light) |
| `000123-6b66` | 0.0590% | light present |
| all seven others | 0.0009-0.0039% | properly dark |

## Results

Final image: MCV min-entropy (SP 800-90B 6.3.1, worst of all 45 pairs, `../analyze_mcv.py`).
Window: `../analyze_preview.py`, whole-window digest structure. AE state from
`ae_before_lock` in each capture.log.

| Run | digital_gain | Window | Distinct | Live | Final MCV | vs 256 |
|---|---|---|---|---|---|---|
| `000117-934f` | 3.25 | 50 | **1** | 0 | **389** | **1.5x** |
| `000025-934f` | 3.25 | 50 | **1** | 0 | 496 | 1.9x |
| `000212-934f` | 3.25 | 50 | **1** | 0 | 1,110 | 4.3x |
| `000412-6b66` | 3.625 | 50 | 3 | 2 | **177** | **0.69x** |
| `000236-6b66` | 3.625 | 50 | 3 | 2 | **190** | **0.74x** |
| `000523-6b66` | 3.625 | 48 | 4 | 3 (one cached x2) | 432 | 1.7x |
| `000123-6b66` | 3.625 | 48 | 3 | 2 | 24,754 | 96x (light) |
| `000450-a92a` | 3.625 | 42 | 5 | 4 | 27,576 | 107x |
| `000038-a92a` | 3.625 | 44 | 4 | 3 | 248,977 | 972x (light) |

### Preview-zero is reproducible, and its floor keeps dropping

All three 2W dark runs again returned a window of fifty byte-identical black frames --
digest `6f77f852…`, `content_changes: 0` -- making **six of six** dark runs on this unit
across two boots and two rounds. The seed rested on the final image alone each time, and
**389 bits (1.52x) is the thinnest total-chain margin measured anywhere in this work.**
The six preview-zero finals to date: 2,969, 1,110, 550, 517, 496, 389. Nothing was changed
between sessions; the lower tail is walking toward 256 by pure repetition.

### The gain knife-edge held on every unit

The 2W sat at digital gain 3.25 in all three runs -- as in every one of its recorded dark
sessions -- and produced constants. The Rev 1.3 and the Plus sat at the 3.625 rail and
produced live frames, as in every one of theirs. The correlation (railed -> live frames,
below rail -> constant) is now unanimous across all recorded dark sessions on four units,
two rounds and multiple boots. It remains a correlation over n=4 units, confounded with
board family, sensor unit and enclosure.

### Dark-window live-frame caching, now in retained data

`000523-6b66`'s window holds live digest `e9ed1361` in **two slots**. Distinct live frames
in these conditions differ in hundreds of bytes, so two independent reads reproducing all
230,400 bytes is impossible in practice; this is a cached buffer re-returned by the
single-core board -- the same stall demonstrated by the lit-run scattered repeats
(`data3/000630`) and absent on the quad-core 2W, now observed in a dark window in
provenance-recorded data.

### The live frames themselves thin with the scene

Within-run live-live MCV, worst pair: 469 bits (`000412`), 1,183 (`000236`), 1,428
(`000523`), 4,034 (`000123`, light). **469 bits across 375 changed bytes is the lowest
per-read novelty measured** -- the same dark scene that thins the final image thins the
live frames' variation. The common-cause failure operates within the preview layer, not
just between layers.

### The Plus: first preview measurement on the 320x320 geometry

Both Plus windows held live frames (4-5 distinct) with the unit railed at 3.625 -- and its
constant is `b71fb8a8…`, which is `sha256((0,0,0,255) x 102400)`: the 320x320 sibling of
the 240x240 constant, equally computable from the panel size alone. Its live frames are
the same near-binary green plane (99.7% of pixels). Loop rate 8.51-9.08 fps -- the slowest
measured (320x320 RGBA on a single core) -- so filling 50 slots takes ~5.5-5.9 s and both
windows arrived under-filled (44, 42). Short windows are the norm on the larger panel.
Final images stay orders of magnitude above the line even in the properly-dark-band run
(27,576): high per-read flicker is a property of this unit, not of stray light alone.

## Combined accounting

Same conventions as `data3/RUNS.md`: distinct live frames x that run's worst within-run
live-live MCV; constants, cached duplicates, CPU serial at zero; `time.time()` (~25-30
bits, estimated not measured) excluded. **Every credit below is a within-run measurement --
this round needed no cross-run analogy anywhere.**

| Run | Preview (measured) | Final | Total | Clears 256? |
|---|---|---|---|---|
| `000117-934f` | 0 | 389 | **389** | yes, 1.5x |
| `000025-934f` | 0 | 496 | **496** | yes, 1.9x |
| `000212-934f` | 0 | 1,110 | **1,110** | yes, 4.3x |
| `000412-6b66` | 2 x 469 = 938 | 177 | **1,115** | yes, 4.4x |
| `000236-6b66` | 2 x 1,183 = 2,366 | 190 | **2,556** | yes, 10.0x |
| `000523-6b66` | 3 x 1,428 = 4,284 | 432 | **4,716** | yes, 18x |
| `000123-6b66` | 2 x 4,034 = 8,068 | 24,754 | 32,822 | yes, 128x (light) |
| `000450-a92a` | 4 x 4,618 = 18,472 | 27,576 | 46,048 | yes, 180x |
| `000038-a92a` | 3 x 982 = 2,946 | 248,977 | 251,923 | yes, 984x (light) |

`000412-6b66` is the thinnest **two-layer** run measured (1,115 total): a sub-256 final
image rescued by two live frames carrying the lowest novelty yet seen. The thinnest totals
overall remain the preview-zero runs, where the total *is* the final image.

Standing caveats, unchanged: MCV over-estimates the floor on non-IID data; multiplying a
pairwise figure by frame count overstates; summing layers assumes an independence the
coupling measurements show is imperfect. Every figure above leans optimistic, which
matters most for the 1.5x and 1.9x rows.

## Retained

All nine runs, in full. No selection criterion was applied; the two light-present runs are
flagged rather than removed.
