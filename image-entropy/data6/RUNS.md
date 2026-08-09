# Sixth round, 2026-08-08: dim-illumination ladder

Ten runs, one boot, elapsed-time names `000037` through `001447`: five illumination levels,
two runs each, captured in descending-light order. This round measures the previously
unmeasured middle of the illumination axis (the IE-L-14 gap): everything between ordinary
room light and no light at all.

| Runs | Unit | Board | Image | Provenance |
|---|---|---|---|---|
| all ten (`-6b66`) | `6b665e1fa1d5` | Pi Zero Rev 1.3 | `59ea2885` | `PROVENANCE-round6-pi0.txt` |

The image is the same build data5 recorded. It predates the capture rig's no-seed
kill-switch (added 2026-08-07); the kill-switch sits downstream of every capture write, so
measurement validity is unaffected, but this build can still derive a seed and is handled
as lab equipment only. Standing rule: cite every run with its `data6/` prefix; run names
collide across `dataN/` directories.

## Scene and method

Same bookshelf as `data1`'s lit baseline, device resting. The room was lit by multiple
fixed lights of different intensities and locations; the levels were produced by
progressively switching lights off, nearest to the shelf first, so the shelf was visibly
dimmer to the operator's naked eye at each level. At level 4 only the farthest light
remained; at level 5 no lights were on anywhere in the house (lens open — this is a dim
condition, not a sealed one). No light-meter readings were taken; the illumination axis is
recovered in-band below.

## Visibility is recoverable in-band

The preview dumps are the exact buffers the panel displayed (the preview path applies no
contrast processing), so "what the operator could see" is measured, not recalled.
Green-channel stats over each run's dumped window, and the resulting labels:

| Level | Runs | preview mean | preview max | Label |
|---|---|---|---|---|
| L1 | `000037`, `000157` | 28.7 | 234–249 | clearly visible |
| L2 | `000407`, `000528` | 5.7–6.7 | 221–237 | visible, dim |
| L3 | `000755`, `000915` | 2.0 | 244–252 | barely visible: isolated highlights only |
| L4 | `001032`, `001158` | 0.06–0.08 | 20–29 | effectively black (a handful of near-black pixels) |
| L5 | `001331`, `001447` | 0.00–0.05 | 3 and 0 | black; `001447`'s window is entirely the all-zero constant |

Contact sheet: `preview_ladder_as_shot.png` — one middle-index dumped preview frame per
run, as shot, no amplification, two rows of five in capture order.

## Results

Final image: MCV min-entropy (SP 800-90B 6.3.1, worst of all 45 pairs,
`../analyze_mcv.py`). Window: `../analyze_preview.py`. AE state from `ae_before_lock` in
each capture.log. A 24-word seed needs 256 bits.

| Run | Level | digital_gain | Window | Distinct | Worst live-live pair | Final MCV | vs 256 |
|---|---|---|---|---|---|---|---|
| `000037` | L1 | 3.625 | 50 | 48 | 184,328 | 1,006,261 | 3,930x |
| `000157` | L1 | 3.625 | 50 | **50 of 50** | 183,766 | 1,485,080 | 5,801x |
| `000407` | L2 | 3.625 | 48 | 43 | 61,462 | 809,617 | 3,162x |
| `000528` | L2 | 3.625 | 39 | 37 | 57,512 | 818,439 | 3,197x |
| `000755` | L3 | 3.625 | 41 | 39 | 23,214 | 451,756 | 1,764x |
| `000915` | L3 | 3.625 | 22 | 21 | 22,114 | 486,903 | 1,901x |
| `001032` | L4 | 3.625 | 43 | 34 | **0** (4 values changed) | 13,213 | 51x |
| `001158` | L4 | 3.625 | 28 | 19 | **0** (6 values changed) | 12,778 | 49x |
| `001331` | L5 | 3.625 | 41 | 2 | n/a — one live frame | 931 | 3.6x |
| `001447` | L5 | 3.625 | 48 | 1 | n/a — zero live frames | 1,283 | 5.0x |

`001331`'s only pairing is live-vs-constant (24.08% changed, 90,583 bits): that is the
quantization-threshold crossing, excluded from layer accounting per IE-M-10.

### The illumination axis is a cliff, not a slope

Every level with any visible content clears the requirement by three orders of magnitude
(L3, barely visible, still 1,764x). The collapse happens between L3 and L4, exactly where
the final image's share of pixels at or above value 4 crashes from 25% to 0.03–0.05% — a
~400x empty gap in a deliberately dim ladder. L4–L5 margins (49x down to 3.6x, with MCV
leaning optimistic precisely there) are the luck-governed regime previously seen only at
blackout.

### Distinct is not thick

The L4 windows hold 19 and 34 distinct digests whose worst live-live pairs carry **zero
bits** (4 and 6 changed values). Dozens of distinct frames, no pairwise novelty: the
cleanest demonstration yet that distinct-digest counts and entropy are different axes, and
that preview credit must be computed from live-live MCV, never from distinctness alone.

### Preview collapse without a seal, on a railed unit

`001447` returned a window of 48 identical all-zero constant frames — the preview-zero
state — and `001331` was 40 constants plus a single green-quantization-plane frame (55,488
green values, max 3). Both previously observed only under a physical seal, and
preview-zero only on the below-rail unit; here they occur with the lens open, in a house
with the lights off, on the unit that rides the gain rail. Digital gain locked at 3.625 in
every run of the ladder, identical to the lit bookshelf baseline: auto-exposure is blind
across the entire measured axis (the one-directional-tell finding, now spanning dim).

### Cached doubles continue

Adjacent-slot byte-identical non-constant doubles appear at every lit level (`000037`
slots 41/42, `000407` 16/17 and 42/43, `000528` 3/4 and 37/38, `000755` 16/17, `000915`
7/8) — the single-core cached-buffer re-return pattern from data3–data5, still present in
dim conditions.

### Window heterogeneity: the AE ramp is in the early slots

In the L2–L3 windows the first dumped frames are near-black (0.06–0.24% nonzero) with
content arriving over the next frames as auto-exposure converges after stream start. Early
window slots under-represent the level; late slots represent it. Whole-window statistics
above include the ramp.

## Limitations

One unit, one scene, two runs per level, no independent light measurement (levels are
ordinal, defined by the operator's switch-off sequence and recovered in-band). MCV
over-estimates the floor on non-IID data (evidence §1, IE-L-01), which matters most for
the L4–L5 rows. The below-rail unit was not run on this ladder. Frames outrank this
manifest; this manifest outranks any summary of it.
