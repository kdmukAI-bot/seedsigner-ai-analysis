# Dark-capture runs, 2026-08-05

Instrumented v0.8.7, upstream-pinned build (app `0.8.7` @ `e0a80d4b`, OS `v0.8.7` @ `d1385939`,
patch `f1c059df`). Lens occluded. Four physical units, identified by `unit_id` (truncated
SHA-256 of the CPU serial) rather than by board model, because two of the units are the same
model.

| unit_id | Board | Panel | Still | Enclosure |
|---|---|---|---|---|
| `934f1769250d` | Pi Zero 2 W Rev 1.0 | 240x240 | 480x480 | Orange 3D-printed case |
| `6b665e1fa1d5` | Pi Zero Rev 1.3 | 240x240 | 480x480 | Milled aluminum case; tightest camera-aperture fit of the four |
| `074c518d70fb` | Pi Zero W Rev 1.1 | 240x240 | 480x480 | None; camera ribbon taped to the back of the bare board |
| `a92ac791f26b` | Pi Zero W Rev 1.1 + Plus display | 320x240 | 640x640 | Large oval 3D-printed Plus-style case |

The enclosure is part of the measured system in every dark run -- it is the first light
barrier the lens sees -- and nothing on a device records it, so it is recorded here (from
the operator's description; photographed camera-side up as photo 03 in the gitignored
`../capture-rig/photos-raw/`, to be cropped into `../figures/`). One observation, hedged
because two runs per unit cannot establish it: the mapping is *consistent with* the
dark-run ordering rather than explanatory of it. The tightest-fitting case belongs to the
unit that reached 173 bits, and the roomiest belongs to the Plus unit whose residual
internal light kept it two orders of magnitude higher. The gel-pack seal at the lens face
remains the demonstrated driver; case fit is a supporting condition.

## Occlusion method

Nothing on the device records how the lens was occluded, so it is recorded here.

**Properly-dark runs:** the device was wrapped in black cloth and placed inside an insulated
cooler bag, with the power cord exiting at the end of the zipper. This was the darkest
arrangement achievable, and it is what separates this round from the earlier captures, whose
"blacked out" condition now looks like the light-present group below.

**Two caveats on that method:**

- **It plausibly traps heat.** Sensor dark current rises with temperature, so an insulated
  enclosure may work against the thing being measured: removing light while increasing thermal
  noise. **Unmeasured** -- no run carries temperature telemetry, and nothing here isolates it.
- **The cord exit is the residual aperture.** The zipper cannot close fully around the cable,
  so the enclosure is not light-tight by construction. That is the most likely path for any
  remaining stray light, and it is consistent with the edge gradients that persist in some
  retained runs (1.39-1.41x on two of the `6b665e1fa1d5` captures).

### Refrigerator: a better light seal, not a temperature experiment

Run `burst-19700101-000207` is the best occlusion in the dataset. Two things produced it, and
neither is refrigeration:

1. **A conformable seal directly at the lens.** The device was sandwiched between two
   **room-temperature** gel ice packs: one inside its fabric sleeve on the shelf, the device
   resting camera-down on top of it, and a second bare pack laid over the device. A gel pack
   deforms to the contour of the enclosure's face and closes the gap around the lens far better
   than a flat surface or cloth alone. The packs are sealing material, not coolant. **This is
   the part that matters, and it is the part to copy.**
2. **A light-tight outer enclosure with no cable breach.** A domestic refrigerator, with the
   battery pack inside so the door gasket closed completely. Any container with a gasket and a
   self-contained power source would serve.

**Temperature is not what is being measured, and the data does not support it as the driver.**
The gel packs were at room temperature, used as sealing material rather than coolant. The two
runs differed in fridge time: `000207` was in briefly and did not cool, while `000409` sat for
several minutes and was at its coldest. **If temperature drove the effect, the cooled run should
have gained more. It gained less** -- 2.2x against 3.1x. That is two runs and not proof, but it
points at the seal rather than the cold.

| Run | Method | Mean px | pixels >= 4 | Gradient | MCV min-entropy |
|---|---|---|---|---|---|
| `000151` | cloth + cooler bag | 0.338 | 0.0026% | 1.02x | 1,297 bits |
| `000207` | refrigerator | 0.337 | 0.0017% | 1.01x | **423 bits** |

The seal change has now been applied to **two units independently**, and both moved the same
way. The changed-value count is the cleanest view, since with a modal difference of zero the
bit figure is essentially that count times 1/ln2:

| Unit | Method | Values changed, worst pair | MCV |
|---|---|---|---|
| `6b665e1fa1d5` | cloth + bag | 312 (0.0451%) | 384 |
| `6b665e1fa1d5` | gel + fridge | **152 (0.0220%)** | **173** |
| `074c518d70fb` | cloth + bag | 979 (0.1416%) | 1,297 |
| `074c518d70fb` | gel + fridge | **341 (0.0493%)** | **423** |

Roughly half as many values move under the better seal, on both boards. This is stronger than
the single-unit comparison that preceded it, though still two units and one run each: within-unit
run-to-run variance under one unchanged method is large (`6b665e1fa1d5` gave 384, 1,958 and
2,527 across three cooler-bag runs), so a repeat of each gel-pack run is what would settle it.

**Sensor temperature remains untested, deliberately.** Dark current rises with temperature, so
a heat-soaked sensor should read higher and a cold one lower, but no run here isolates it: none
carry temperature telemetry and none were held long enough to equilibrate.

Testing it properly is not just a matter of using a freezer. **Cycling a camera through a large
temperature change condenses moisture inside the lens assembly**, where it is difficult to
remove and where it wrecks the measurement it was meant to inform: moisture between elements
scatters light and alters the optical path, so the result characterises fog rather than sensor
noise. The risk is worst on the return to ambient.

A safe protocol would seal the device with desiccant in an airtight container **before** the
temperature change, equilibrate fully at the target temperature, capture without opening (the
battery-inside arrangement above already allows this), and let it return to ambient still
sealed. Until someone does that, temperature is an uncontrolled variable in every figure here,
and the direction of its effect is inferred from physics rather than measured.

The defensible conclusion from this run is narrower and still useful: **a fridge door with the
power source inside is the most reliable light seal available without building one**, and it
reproduces the ~400-bit result on a second unit.

## Selection criterion: the device's own review screen

Runs were not sampled blind. In each setup the capture was **repeated until the final-image
review screen displayed pure black** -- that is, until the `autocontrast(cutoff=2)` the review
screen applies found nothing to stretch. Anything visible on screen meant light was still
getting in, and the run was redone. Usually several attempts per setup.

This is a genuinely useful field instrument: it needs no analysis and runs on the device.
Simulating it over every retained final (`../analyze_review_screen.py`, Pillow 11.0.0 -- the
version SeedSigner OS v0.8.7 ships via buildroot `bf2a2858`; results byte-identical under
11.1.0):

| Run | Method | Finals displaying an image | MCV |
|---|---|---|---|
| `000409` | gel + fridge | 2 of 10 | **173** |
| `000207` | gel + fridge | 0 of 10 | 423 |
| `000151` | bag | 0 of 10 | 1,297 |
| `000049` | bag | 1 of 10 | 1,775 |
| `000345` | bag | 2 of 10 | 1,958 |
| `000126` | bag | 3 of 10 | 384 |
| `000255` | bag | 6 of 10 | 2,527 |
| `000241` | bag | 10 of 10 | 34,024 |
| `000427` | bag | 6 of 10 | 36,462 |

**Amendment 2026-08-06: an earlier version of this table classified each run as "pure black"
or "stretched". Recomputing per frame at the shipped Pillow version shows a run-level label is
not well-defined -- the display class flickers between consecutive finals of one unchanged
setup (`000409`, the 173-bit run: 8 black, 2 stretched) -- so the table now records per-frame
counts, and the run-level classification is retired.**

**Two consequences, and the second matters more.**

First, the criterion itself flickers. The operator protocol keyed on a single displayed still,
and consecutive finals from one unchanged setup fall on both sides of the identity threshold.
A run cannot be cleanly classed as passing or failing the criterion; `000126` (3 of 10
stretched, 384 bits) sits in the same flicker band as runs the protocol accepted, and still
should not be quoted as a clean dark measurement.

Second, and load-bearing for the analysis: **the display bounds the entropy in neither
direction.** Finals that display pure black occur in runs spanning **173 to 1,958 bits, a
factor of 11**, and finals that display a faint image occur in this round's 384-bit run -- and,
in the face-down series, in runs measuring as low as **113 bits** (`../data3/RUNS.md`,
`000150-6b66`: 2 of 10). A pure-black review screen confirms light was excluded; a faintly
visible one certifies nothing. An operator cannot tell 173 from 1,958 by looking, and can be
shown an image by a capture in the lowest class measured.

## Two populations, not a continuum

Occlusion quality split the runs into two clearly separated groups. The discriminator is the
share of pixels at or above value 4 in the first frame, which differs by 10-20x between them:

| Group | pixels >= 4 | p99.99 | AE digital gain |
|---|---|---|---|
| Properly dark | 0.001 - 0.007% | 2 - 3 | 3.625 (at ceiling) |
| Light present | 0.048 - 0.166% | 5 - 7 | 1.102 |

**Only the properly-dark group is retained.** The runs with light present are not failures of
the device; they are failures of the occlusion, and they inflate the entropy estimate because
stray light contributes shot noise. Keeping them would make the floor look better than it is.

## Retained

A 24-word seed needs 256 bits. All figures are the final image alone; every run also chained
preview frames, which are excluded throughout as the conservative choice.

| Run | unit_id | Method | pixels >= 4 | Gradient | MCV (all pairs) | vs 256 |
|---|---|---|---|---|---|---|
| `burst-19700101-000409` | `6b665e1fa1d5` | **gel + fridge** | 0.002% | 1.00x | **173** | **0.68x** |
| `burst-19700101-000126` | `6b665e1fa1d5` | bag | 0.001% | 1.01x | 384 | 1.50x |
| `burst-19700101-000207` | `074c518d70fb` | **gel + fridge** | 0.002% | 1.01x | 423 | 1.65x |
| `burst-19700101-000151` | `074c518d70fb` | bag | 0.003% | 1.02x | 1,297 | 5.1x |
| `burst-19700101-000049` | `934f1769250d` | bag | 0.001% | 1.00x | 1,775 | 6.9x |
| `burst-19700101-000345` | `6b665e1fa1d5` | bag | 0.002% | 1.41x | 1,958 | 7.6x |
| `burst-19700101-000255` | `6b665e1fa1d5` | bag | 0.001% | 1.39x | 2,527 | 9.9x |
| `burst-19700101-000241` | `a92ac791f26b` | bag | 0.007% | 1.13x | 34,024 | 132x |
| `burst-19700101-000427` | `a92ac791f26b` | bag | 0.004% | 1.04x | 36,462 | 142x |

**The best-sealed run measures 173 bits, which is BELOW the 256 a 24-word seed requires.**
Unbounded MCV on the same pair is 219 bits, still below. Only 152 of 691,200 values differ
between the worst pair, across 12 distinct difference levels, almost all of them +/-1.

Three runs on two units now sit at or near the requirement: 173, 384 and 423 bits. Earlier
rounds reported 6x to 52x on nominally the same condition; those runs were not fully dark, and
stray light was inflating them. Since most-common-value **over**-estimates the floor on non-IID
data, the true min-entropy of these pairs is lower still than the figures shown.

Scope, stated precisely: this is **the final image alone**. Every run above chained 50 preview
frames that these figures exclude, so the seed generated in each session had substantially more
input than the number reported. A 12-word seed needs 128 bits, which 173 still clears at 1.36x.

Reaching this condition was believed to take deliberate effort -- a conformable seal at the
lens inside a gasketed enclosure. **Refuted 2026-08-06 by `../data3`:** face-down runs on a
shadowed desk, no seal and no enclosure, produced final images inside this same
properly-dark pixel band measuring **113 and 221 bits** (`data3/burst-19700101-000150-6b66`,
`data3/burst-19700101-000303-6b66`; further sub-256 finals of 177 and 190 in `../data4`).
113 is *below* this round's best-sealed 173: the engineering bought reliability of the
state, not the state itself; ordinary shadow reaches it unaided. (The preview-frame
exclusion also matters less than assumed: in those runs the chained preview window
collapsed to near-constant black, or to a single known constant outright. See
`../data3/RUNS.md` and `../data4/RUNS.md`.)

The Plus unit (`a92ac791f26b`) sits two orders of magnitude higher because it cannot be made as
dark: its residual internal light is itself signal. Its apparent advantage is a light leak.

Three runs are kept for `6b665e1fa1d5` and two for `a92ac791f26b` deliberately: they are the
only measurements of **run-to-run variance on one device under nominally identical conditions**,
and that variance is large (384 to 2,527 bits, 6.6x, on one unit). A single run cannot show it.

## Deleted

Seven runs, every one from the light-present group. Their frames are gone; their summary
statistics are recorded here because the effect they demonstrate is worth keeping:

| Run | unit_id | pixels >= 4 | Edge gradient |
|---|---|---|---|
| `burst-19700101-000024` | `6b665e1fa1d5` | 0.048% | 1.36x |
| `burst-19700101-000026` | `6b665e1fa1d5` | 0.105% | 1.60x |
| `burst-19700101-000028` | `074c518d70fb` | 0.077% | 1.20x |
| `burst-19700101-000031` | `074c518d70fb` | 0.068% | 1.20x |
| `burst-19700101-000044` | `a92ac791f26b` | 0.160% | 1.21x |
| `burst-19700101-000210` | `a92ac791f26b` | 0.159% | 1.19x |
| `burst-19700101-000344` | `a92ac791f26b` | 0.166% | 1.34x |

An eighth run was **lost, not deleted**: a Plus capture with a pronounced directional leak
(mean 0.477, max 26, edge gradient 1.54x, digital gain 1.10) measured 268,794 bits, 1,049x --
roughly 7.5x the clean Plus figure. It was overwritten during an import (see below) before it
could be preserved. It remains the clearest example of the central hazard: **contamination in
a dark run inflates the floor, so the failure mode is a reassuring wrong answer, not an
alarming one.**

Three lit bookshelf runs (`000029`, `000111`, `000303`) were also deleted from this directory
as byte-identical duplicates of the copies in `../data1`.

## Run names collide across devices

The devices have no real-time clock, so every boot starts at `1970-01-01 00:00:00` and runs are
named by elapsed time since boot. **Two devices doing a run at a similar point after power-on
produce the same directory name.** Importing a second card over the first silently overwrites
it, which is how the leaked Plus run above was lost. Import into a per-unit destination, or
rename on import to include the `unit_id`.
