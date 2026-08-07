# Preview-layer runs, 2026-08-06

The first runs to measure the preview-frame layer -- the rolling window of up to 50 frames
the entropy hash chains ahead of the final image, which every earlier figure excluded.
Eight runs, two boards, both on upstream-pinned instrumented builds of v0.8.7.
Replications and a third display geometry: `../data4/RUNS.md`.

## Provenance

| Runs | Unit | Board | Patch | Image | Provenance file |
|---|---|---|---|---|---|
| `000031`, `000150`, `000303`, `000630` (`-6b66`) | `6b665e1fa1d5` | Pi Zero Rev 1.3 | `21dd1fd3` | `59ea2885` | `PROVENANCE-round2-pi0.txt` |
| `000025`, `000117`, `000202`, `000322` (`-934f`) | `934f1769250d` | Pi Zero 2 W Rev 1.0 | `21dd1fd3` | `ac52e24e` | `PROVENANCE-round3-pi02w.txt` |

App and OS identical on both: `0.8.7` @ `e0a80d4b`, `v0.8.7` @ `d1385939`, both
upstream-verified. Run directories carry a unit suffix stamped on-device (first 4 hex of
`unit_id`), because the devices have no real-time clock and name runs by elapsed time
since boot, so two devices can collide. Elapsed-time names also recur across boots of the
SAME unit: always cite runs with their `dataN/` directory prefix (see `../data4/RUNS.md`
for a live example of the collision).

## Conditions

Dark runs: face-down (camera-down) at one position on the operator's desk, chosen to sit
in shadow from the two closest light sources; three consecutive runs per board, device not
lifted or repositioned between them, minutes apart on one boot -- so they isolate
same-scene, new-session variance. One lit control per board (`000630`, `000322`), ordinary
lit scene. Sensor temperature unmeasured. AE state was byte-identical across each board's
dark runs (`exposure_speed=32978`, `analog_gain=1.1875`); digital gain differed BETWEEN
boards -- see "The gain knife-edge" below.

## The loop rate, measured

These are the first runs anywhere to measure how fast the preview layer actually fills.
Patch `21dd1fd3` logs per-append timing.

| Run | Board | Loop fps | Median gap | Warm-up | Window span | Distinct |
|---|---|---|---|---|---|---|
| `000031-6b66` | Zero | 11.15 | 0.0914 s | 0.214 s | 4.332 s | 2 of 50 |
| `000150-6b66` | Zero | 11.39 | 0.0888 s | 0.211 s | 4.278 s | 5 of 50 |
| `000303-6b66` | Zero | 11.13 | 0.0910 s | 0.172 s | 4.425 s | 2 of 50 |
| `000630-6b66` (lit) | Zero | 11.12 | 0.0911 s | 0.206 s | 4.368 s | **46 of 50** |
| `000025-934f` | 2 W | 14.08 | 0.0713 s | -- | 3.479 s | **1 of 50** |
| `000117-934f` | 2 W | 13.88 | 0.0713 s | -- | 3.516 s | **1 of 50** |
| `000202-934f` | 2 W | 14.00 | 0.0713 s | -- | 3.479 s | **1 of 50** |
| `000322-934f` (lit) | 2 W | 14.05 | 0.0713 s | 0.171 s | 3.494 s | **50 of 50** |

**The display loop runs at 11.1 fps on the Pi Zero and 14.0 fps on the 2 W** -- under half
the camera's configured 24 fps in both cases. Filling all 50 slots takes ~3.5-4.4 s;
camera warm-up is only ~0.2 s. This refuted the prediction registered before the run
(25-35 fps, the loop outpacing the camera) in both directions.

The lit controls settle the structural question directly: **46 of 50 distinct on the
Zero, 50 of 50 on the 2 W** -- in a lit scene the layer delivers essentially the 50
distinct frames the design assumes. The Zero's four repeats (indices 3, 5, 30, 42,
scattered) are capture-thread stalls from single-core contention: on one core the display
loop and `PiVideoStream.update()` compete, occasionally leaving `self.frame` unrefreshed
between polls. The corroborating evidence is the gap jitter (39 ms on the Zero against
4 ms on the 2 W) and the 2 W's zero repeats at delivery 14.03 fps against a loop of
14.05. Two distinct live frames differ in only 0.36-0.44% of their bytes, so two
independent sensor reads reproducing all 230,400 bytes exactly is impossible in practice:
byte-identical live frames in separate slots are cached buffers, not separate exposures.
(A dark-window instance of the same caching appears in `../data4/RUNS.md`, run
`000523-6b66`.) The slots are therefore not guaranteed to be separate sensor reads, on
any board, in any scene.

## Dark scenes: the window is dominated by a known constant

Units note: `Constant-black` counts SLOTS; `Distinct` and `Live` count distinct digests.
The two need not sum to the window: `000150`'s four live frames occupy five slots (one live
digest cached into two adjacent slots, the same single-core re-return documented under the
loop-rate section), and `000031`'s single live frame occupies two.

| Run | Window | Distinct | Constant-black | Live | Final image MCV | vs 256 |
|---|---|---|---|---|---|---|
| `000031-6b66` | 50 | 2 | 48 | 1 | 26,318 | 102x (light present) |
| `000150-6b66` | 50 | 5 | 45 | 4 | **113** | **0.44x** |
| `000303-6b66` | 50 | 2 | 49 | 1 | 221 | 0.86x |
| `000025-934f` | 50 | **1** | **50** | **0** | 2,969 | 11.6x |
| `000117-934f` | 50 | **1** | **50** | **0** | 550 | 2.1x |
| `000202-934f` | 50 | **1** | **50** | **0** | 517 | 2.0x |

The constant is byte-identical pure black (RGB all 0, alpha 255) with the SAME digest
(`6f77f852…`) in every dark run on both boards -- and it is computable without ever
touching a device: `sha256((0,0,0,255) x 57600)` reproduces it exactly from the panel
size alone. Content an attacker already has contributes nothing: every repeated slot is
zero bits. This is content collapse on the video-port path (240x240 RGBA, no JPEG stage):
the pipeline quantizes the light-starved scene to zero. The repeats come in long unbroken stretches
(47 of 49 consecutive pairs identical in `000031`), unlike the lit run's scattered
stalls, so the dark collapse is quantization, not oversampling.

**On the 2 W the preview layer contributed exactly zero, three times.** The entire
50-slot window was one attacker-computable frame (`content_changes: 0`, verified from the
dumped frames, not only the log). The seed rested on the final image alone: 517 and 550
bits in two of the three runs. This is the demonstration -- not an inference -- that the
layered design is single-layer in a dark scene, and reaching that state took a desk in
shadow. Combined with the held-button path (which drops the layer to zero frames
deterministically; see `image-entropy-v087-instrumented-findings.md` in the seedsigner
knowledge docs), there are two independent routes to a one-layer chain, neither requiring
intent or equipment. Replication: three further preview-zero runs, and a 389-bit final,
in `../data4/RUNS.md`.

**The final image fell below the 256-bit requirement with no engineering.** 113 and 221
bits, on a desk, in ordinary shadow -- and 113 is *below* the 173 bits that a gel-pack
seal inside a refrigerator produced in `../data2`. The engineered condition was never a
floor; it was a laborious way to reach a sensor state that ordinary shadow reaches
unaided (`data2/RUNS.md` carries the amendment). `000031` is retained but flagged: its
first-frame pixel statistics (0.048% of values >= 4) sit in the light-present band by the
`data2` discriminator, so its 102x is inflated by stray light and is not a dark
measurement. Same-configuration session variance is enormous: 26,318 against 113 and 221,
minutes apart, with nothing moved.

## The gain knife-edge

In identical darkness the two boards' auto-exposure settled at different digital gains,
stably across every recorded session: the Zero at 3.625 (the rail), the 2 W at 3.25. The
board at the rail produced live frames in every dark window; the board below it produced
only the constant, in every dark window. A live frame is the green plane's mean crossing
the video-port rounding threshold, and an 11.5% gain difference is exactly the kind of
multiplier that puts one unit just above that knife edge and the other just below. The
correlation is unanimous across all recorded dark sessions on four units (see
`../data4/RUNS.md`), but it is a correlation over four physical units, confounded with
board family, sensor unit and enclosure. The design controls neither variable: which
layer is thin in the dark is decided by per-unit accidents the code never inspects.

## What a live frame actually is

Re-derived from `000150-6b66`'s four dumped live frames (window indices 18, 19, 39, 42).
A live frame is not a noisy image; it is a **near-binary green plane**: frame18 has
57,254 nonzero bytes, every one of them green (values: 57,233 ones, 20 twos, one 4),
covering 99.4% of pixels, with 346 pixels held back at zero. Green crosses first because
it has twice the Bayer photosites and unity AWB gain while red and blue are scaled from a
smaller base. The frame is one global event -- the green plane crossing the rounding
threshold -- and the information is in the minority that did not cross, plus which pixels
flip between reads:

- **Adjacent live frames differ in 820-1,004 bytes (0.36-0.44%).** Worst within-run
  live-live MCV: **1,078 bits** (min of 6 pairs). That is the honest per-frame scale of
  the layer's contribution; live-vs-constant MCV (~92-94k) is dominated by the global
  threshold crossing and must not be used for accounting.
- **Not one position is consistently held back**: across the four live frames the union
  of held-back pixels is 1,728 positions, and the intersection is **0**. The volatile
  component is fully per-read; there is no unit-specific replayable signature in it.

## Combined accounting: what the seed actually rested on

v0.8.7 builds the seed as a sequential SHA-256 chain (`tools_views.py`): CPU serial, then
`str(time.time())`, then one step per preview frame, then the final image. Two structural
consequences decide the arithmetic: **a repeated frame contributes exactly zero** (re-
feeding identical bytes is deterministic given the previous state), and **the output is
capped at 256 bits**, so the question is whether the input clears 256. The CPU serial is
counted as 0 (a fixed device property); `time.time()` on a board with no RTC is
seconds-since-boot, worth perhaps 25-30 bits against a realistic attacker window --
estimated from mechanism, not measured, and excluded from the totals.

Preview credit: distinct live frames x that run's worst within-run live-live MCV.
Constants and cached duplicates at zero. Runs holding a single live frame have no
within-run pair, so they are credited at the worst cross-run dark live-live figure
computed over this round's retained frames -- an estimate by analogy, marked as such
(`000303`'s frame37 x `000150`'s frame18 = 764 bits; `000031`'s frame29 worst pair =
1,651 bits).

| Run | Preview | Final | Total | Clears 256? |
|---|---|---|---|---|
| `000630-6b66` (lit) | 27 dumped x 184,523 | 1,544,107 | ~6.5 million | yes, overwhelmingly |
| `000322-934f` (lit) | 50 distinct; worst pair 121,791 | 1,332,455 | >1.3 million | yes, overwhelmingly |
| `000031-6b66` | 1 x 1,651 (cross-run est.) | 26,318 | ~27,969 | yes, 109x (light) |
| `000150-6b66` | 4 x 1,078 = 4,312 | 113 | **4,425** | yes, 17x |
| `000303-6b66` | 1 x 764 (cross-run est.) | 221 | **~985** | yes, 3.8x |
| `000025-934f` | 0 | 2,969 | **2,969** | yes, 11.6x |
| `000117-934f` | 0 | 550 | **550** | yes, 2.1x |
| `000202-934f` | 0 | 517 | **517** | yes, 2.0x |

Every run clears 256 -- the thinnest here at 2.0x, and 1.5x in the `data4` replications.
In the run with the lowest final image ever measured (`000150`, 113 bits), the preview
layer is what carried the seed: that is the layered design doing exactly the work it was
designed to do. In the three 2 W runs the design's headline mechanism contributed
nothing at all and the final image carried everything. Either layer can be the one that
carries the seed, and nothing in the code knows which.

The `000303` and `000031` totals rest on a cross-run analogy for a single live frame and
should be read as weaker than the others. The digest-coverage dumping rule is what made
their live frames available at all: `000031` dumped index 29, `000303` index 37, and
`000150` indices 18, 19 and 39 -- rare frames that a positional sampling rule would
miss, which is precisely why the rule dumps a representative of every logged digest.

Caveats that cut against every total above:

- **Adding layers assumes independence, and the layers are measurably coupled** -- weakly.
  Comparing each of `000150`'s live preview frames against the final still of the same
  capture (2x2 block downsample to match geometry), preview-crossed pixels read very
  slightly brighter in the final image than preview-cold pixels: z = 4.0 on all four
  frames, magnitude +0.02%. Statistically detectable, consistent in direction, and
  negligible next to the margins -- but non-zero, and both layers watching the same scene
  through the same gain is the structural reason they thin together.
- **Multiplying a pairwise figure by the frame count overstates**, because conditioning
  on several known frames tells an attacker more than conditioning on one. And MCV
  over-estimates the floor on non-IID data throughout (see
  `entropy-estimator-pitfalls.md`).

## What this establishes, scoped

The layered-chain argument assumed the preview layer supplies ~49 additional noise
realizations when the final image is thin. Measured in the same captures, in the blocked-lens
conditions where the final image IS thin:

- **Count:** 1-5 distinct frames per 50-slot window -- including exactly zero live
  content, three times here and three more times in `data4`. Most slots hold a constant
  the attacker can compute from the panel size.
- **Quality:** each distinct live frame carries genuine per-read variation (nothing in
  the volatile minority repeats), worth ~469-1,428 MCV bits frame-to-frame in the properly
  dark 240px windows across the two rounds (4,618 on the properly dark Plus window; 4,034
  occurs only in a light-flagged run).
- **Net:** the chain held in every measured run, by margins as thin as 1.5-2.0x on an
  estimator that over-estimates, with the carrying layer decided by per-unit accidents.

The failure mode is **common-cause**: both layers view the same dark scene and the
preview path quantizes harder, so they degrade together rather than independently --
and the same darkness also thins the live frames' own per-read novelty. Layer count is
not independence. A window can legitimately deliver zero or one distinct live frames,
and nothing in the code notices.

**No button-holding or engineering is required to reach the state where both layers are
simultaneously thin.** The held-button finding (preview drops to exactly zero frames,
deterministically) remains a defect with a code fix attached, but appending frames cannot
be the whole fix: in these conditions most appended frames would be the known constant or
a cached duplicate. The actionable requirement is an **entropy health check on frame
content** -- distinct-digest count at minimum -- not merely a frame-count guarantee.

Positive scope, stated with equal care: in lit scenes the layer delivers 46-50 of 50
distinct frames and final images measure four orders of magnitude above requirement --
the design works exactly as intended in the conditions it was designed around. A 12-word
seed (128 bits) clears in every measured chain here at 4.0x or better on the totals;
the lone sub-128 final image (113) sat in a window holding four live frames.

## Retained

All eight runs, in full. No selection criterion was applied; the light-present run is
flagged rather than removed.
