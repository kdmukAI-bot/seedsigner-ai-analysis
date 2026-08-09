# Running NIST SP 800-90B against the image-entropy captures

Established 2026-08-09, in response to readers citing "NIST standards" against the
image-entropy analysis. Nothing here has been published; it is the record of what a real
SP 800-90B run does to this data, and which of the analysis's asserted caveats it confirms,
quantifies, or contradicts.

Companion device-side findings: `seedsigner/docs/knowledge/entropy-estimator-pitfalls.md`
(the seven ways the estimator misleads) and `image-entropy-v087-instrumented-findings.md`.

---

## The two documents are not interchangeable, and only one of them is relevant

**SP 800-22 Rev. 1a** (April 2010) is a statistical test suite for the *output* of a
generator. It is **not withdrawn** — the "(Withdrawn)" pages that turn up in search results
are the 2001 and 2008 editions. NIST
[announced in April 2022](https://csrc.nist.gov/news/2022/decision-to-revise-nist-sp-800-22-rev-1a)
that it will be revised, and objective #1 of that revision is to *"clarify the purpose and
use of the statistical test suite, in particular rejecting its use for assessing
cryptographic random number generators."* No draft has appeared.

It cannot measure entropy, and NIST says so in two places worth quoting:

- SP 800-22 Rev. 1a, Abstract: *"no set of statistical tests can absolutely certify a
  generator as appropriate for usage in a particular application, i.e., statistical testing
  cannot serve as a substitute for cryptanalysis."*
- SP 800-90B §4.1: *"traditional statistical procedures (e.g., the randomness tests
  described in NIST SP 800-22) that test the hypothesis of unbiased, independent bits will
  almost always fail, and thus are not useful for monitoring the noise source."*

For this feature SP 800-22 is doubly uninformative: every SeedSigner entropy path ends in
SHA-256, so the *output* passes regardless of input quality, while the *input* — a
photograph — fails nearly every test in the suite because natural images are highly
structured. Neither result carries information about the seed. (The "a counter through a
good hash passes SP 800-22" formulation is **not** a NIST statement; its prominent source is
Saarinen, [eprint 2022/169](https://eprint.iacr.org/2022/169). Do not attribute it to NIST.)

**SP 800-90B** (final, January 2018) is the one that applies. It assesses the *raw noise
source*, before conditioning, and it is not merely a battery of tests — see "What 90B asks
for that we do not have" below.

## The data requirements are real, and an image already satisfies them

§3.1.1 item 1: *"A sequential dataset of at least 1 000 000 sample values obtained directly
from the noise source (i.e., raw data) shall be collected for validation."* Concatenating smaller runs is
allowed provided each is ≥1000 samples.

So the reader objection — that these methods need a huge stream — is **correct as stated and
already satisfied**. One 480×480 RGB888 final image is 691,200 bytes. Two frames differenced
against each other exceed the requirement; five disjoint pairs from one ten-frame burst give
3,456,000 samples.

One consequence worth keeping: **a single final image (691,200 samples) is below the
minimum.** `ea_iid`/`ea_non_iid` warn and proceed; `ea_restart` requires *exactly* 1,000,000
and refuses anything else.

## Method used here

NIST's own tool, [usnistgov/SP800-90B_EntropyAssessment](https://github.com/usnistgov/SP800-90B_EntropyAssessment),
built in Docker from the repo's own dependency list. Two scenes on the **same unit**
(`6b665e1fa1d5`, Pi Zero Rev 1.3, 480×480), so scene is the only variable:

- bookshelf — `data1/burst-19700101-000303/stock`
- blank white wall — `data5/burst-19700101-000306-6b66/stock`

**Difference domain is forced to mod-256 here.** 90B requires symbols to fit one byte
(§3.1.3: alphabet ≤ 256; the tool hard-limits `bits_per_symbol` to 1–8). The published
figures use the *signed* domain, which spans −255..255 and does not fit. Mod-256 is the
bijective choice; absolute value folds ±k together and, per the published method notes, moves
the mode off zero on lit series. **Figures below are therefore not directly comparable to the
published signed-domain numbers**, and any recomputation must check its domain first.

Second departure from published methodology: these datasets pool five *disjoint consecutive*
pairs rather than selecting the **worst of all 45 pairs**. That makes them mildly optimistic
relative to the published convention.

## Result 1 — the IID test fails, as the analysis asserted

`ea_iid` on both difference datasets:

```
** Failed chi square tests
** Failed length of longest repeated substring test
** Failed IID permutation tests
```

Both scenes, all three checks. The published claim that "a real SP 800-90B assessment fails
the IID test on this data" is now **verified rather than asserted**, and the non-IID track
(§6.2, minimum over ten estimators) is the correct one.

## Result 2 — `analyze_mcv.py` agrees with NIST's implementation exactly

`ea_iid` reports H via the same MCV estimator (§6.3.1). On the mod-256 difference data:

| Scene | `analyze_mcv.py` formula | NIST `ea_iid` |
|---|---|---|
| bookshelf | 2.4228 | 2.422813 |
| white wall | 2.2006 | 2.200629 |

The published script's confidence-bound arithmetic is correct against the reference tool.

## Result 3 — MCV overstates the floor by 2.0–2.6× on lit series

IE-L-01 says every margin is an over-estimate "by an unquantified amount." On the difference
datasets, per-sample min-entropy (8-bit symbols, literal track):

| Estimator (§6.3) | bookshelf | white wall |
|---|---|---|
| Most Common Value | **2.4228** | **2.2006** |
| t-Tuple | 1.0210 | 1.1082 |
| LRS | 1.4345 | 1.5481 |
| MultiMCW prediction | 0.9448 | 1.4391 |
| Lag prediction | 0.9827 | 1.3609 |
| MultiMMC prediction | 0.9827 | 1.3332 |
| LZ78Y prediction | 0.9827 | 1.3609 |
| **H_I = min(H_original, 8×H_bitstring)** | **0.8156** | **0.9907** |

(Collision, Markov and Compression apply only to binary inputs, so seven estimators appear in
the literal track; all ten act on the bitstring track, which is what `8×H_bitstring` carries.)

MCV is the **highest** of the seven on this data — 2.42 against a 0.94 minimum for the
bookshelf. Whole-frame, at 691,200 samples per frame-pair:

| Scene | published MCV (signed) | full non-IID assessment | vs 256 bits |
|---|---|---|---|
| bookshelf | 1,505,982 bits (5,882×) | ~563,800 bits | ~2,202× |
| white wall | 1,490,163 bits (5,820×) | ~684,800 bits | ~2,674× |

**The headline survives comfortably.** A full ten-estimator assessment lands roughly 2.2–2.7×
below the published MCV figure and still clears a 24-word seed by more than two thousand
times.

One wording correction for the published documents: they say a full assessment takes the
minimum over ten estimators "every one of which can only return a figure at or below this
one." That is true *on this data* but is not guaranteed in general — individual estimators
may exceed MCV. What is guaranteed is that the **minimum** is ≤ MCV, because MCV is one of
the ten.

## Result 4 — the scene-richness intuition is inverted, and the reason is stationarity

This is the finding that answers the reader question, and it is not what either side expects.

Column-major datasets (SP 800-90B §3.1.4.1 shape: walk one photosite down all ten captures,
then move to the next photosite). Consecutive samples are the *same* photosite at different
times, so the static scene cannot contribute — only what changed between captures:

| Dataset | H_I (bits/sample) |
|---|---|
| bookshelf, whole frame | **0.0895** |
| white wall, whole frame | **1.5607** |

A 17× gap in the blank wall's favor. But the underlying physical variation is nearly
identical between the two scenes:

| | bookshelf | white wall |
|---|---|---|
| frame mean level | 67.8 | 133.6 |
| positions that never changed across 10 captures | 1.11% | 0.00% |
| median per-photosite spread | 5 | 4 |
| mean per-photosite spread | 5.60 | 4.05 |
| mean distinct values per photosite (of 10) | 5.25 | 4.57 |

The bookshelf photosites actually vary *slightly more*. So the 17× gap is an **estimator
artifact, not an entropy difference.** Splitting the bookshelf by brightness proves it — same
photograph, same captures, partitioned by mean level:

| Bookshelf subset | share of frame | mean level | H_I |
|---|---|---|---|
| bright band (100–200) | 24.1% | 142.4 | **2.3455** |
| dark band (< 40) | 45.9% | 14.5 | **0.2102** |
| whole frame | 100% | 67.8 | **0.0895** |

**The whole-frame figure is below both of its own sub-bands.** That is the signature of a
non-stationary mixture: forced to describe two very different distributions with one number,
the estimators do worse than on either alone.

And at matched brightness the bookshelf **outscores** the blank wall (2.3455 vs 1.5607). The
bookshelf is not a worse scene. Two things are happening, and they must not be conflated:

1. **Brightness sets per-photosite entropy** — an 11× swing *within a single photograph*
   (0.2102 dark vs 2.3455 bright). This is the photon-shot-noise mechanism the published §2
   describes, now measured with NIST's estimators.
2. **A mixed-brightness scene violates 90B's stationarity requirement.** §3.2.2 #2: *"The
   behavior of the noise source **shall** be stationary."* A busy scene is a patchwork of
   distributions; a uniformly lit blank field is the closest a camera gets to a well-behaved
   90B noise source.

So a properly-run 90B assessment is scene-dependent — in the **opposite direction** from the
folk worry. It penalizes the cluttered scene and rewards the featureless one. The published
conclusion (illumination is the axis, not scene detail) is not merely preserved; it is
sharpened.

**Caveats that must travel with Result 4.** n=1 run per scene, different sessions, different
AE state (the wall run sat at digital gain 2.07). The r=10 column datasets are **not** a
compliant restart test — §3.1.4.1 requires r=1000 — and the burst rig is the *worst case* for
the column direction by construction: its ten frames share one AE lock and sit ~0.59 s apart,
so they are far more alike than ten independent capture sessions would be. Column figures are
biased low for both scenes.

## Full-corpus sweep (2026-08-09)

After the two-scene results above, the assessment was run on **every retained final-image
series, all 42 runs across data1-data6** (including the then-unpublished dim ladder), same
construction per series: mod-256 difference, five disjoint consecutive pairs pooled,
1,000,000 samples, `ea_non_iid -i -a`. Artifacts shipped in the analysis repo:
`image-entropy/analyze_nist90b.py` (dataset builder), `image-entropy/evidence/nist90b-sweep-results.tsv`
(per-series table), `image-entropy/evidence/nist90b-sweep-raw-output.txt` (raw tool output).
The formula MCV cross-check matched the tool on all 42.

Three regimes, cleanly:

| Regime | Runs | Published MCV / NIST floor ratio | NIST floor, whole frame |
|---|---|---|---|
| lit (bookshelf, wall, lit controls, dim L1 bright run) | 9 | **1.9-3.1x** | 493K-1.52M bits (1,925x-5,942x the 256 needed) |
| dim mixed scenes (data6 L1-L3) | 5 | 2.6x-2,476x (mixture artifact, see below) | 182-560K bits |
| dark and effectively-black (data2-data4 dark, L4-L5) | 28 | 1.6x-72x | **9-625 bits** |

**The dark finding is the headline.** Every properly-dark final image falls below 256 bits
under the standardized floor. The six preview-zero chains, whose totals ARE their final
image (the window contributed zero), restate directly, no inference needed:

| Run | Published (MCV) | NIST floor |
|---|---|---|
| data3/000025-934f | 2,969 | 77 |
| data4/000212-934f | 1,110 | 86 |
| data3/000117-934f | 550 | 100 |
| data3/000202-934f | 517 | 64 |
| data4/000025-934f | 496 | 46 |
| data4/000117-934f (the 1.52x headline chain) | 389 | **36** |

**The published 1.52x margin does not survive the standardized floor: the thinnest chain
measures ~36 bits, 0.14x the requirement.** This was always the direction IE-L-01 warned
about; the size is now measured. The published verdict sentence ("every measured chain
cleared 256") is MCV-scoped and had to be amended. Note the pooled-pairs convention is
mildly optimistic, so these floors are still over-estimates.

The sub-256-final runs with live windows (113 -> 64, etc.) are NOT directly restated:
their chains were carried by preview frames, and the preview layer has not been assessed
under the full suite. Chain-level statements there remain inferences.

**The dim-ladder ratios are dominated by the stationarity artifact**, not by entropy
collapse alone: two L1 runs of the same scene minutes apart scored 27K vs 560K under the
floor (MCV differed only 1.4x), and the L3 run with isolated highlights on a black field
hit ratio 2,476x. This is the Result 4 mixture effect at scale: the floor is real but very
not tight on mixed scenes, and run-to-run spread is enormous. Quote dim-regime floors only
with this caveat attached.

t-Tuple/LRS behaved as predicted on dark data (mostly-zero differences are repeated
structure, which they punish): the dark ratios (up to 72x) dwarf the lit ones (~2-3x),
confirming the pitfalls-doc pattern that estimator gaps widen exactly where margins thin.

## What a compliant restart test would take

§3.1.1 item 3 and §3.1.4.1: restart the source **r = 1000** times, collect **c = 1000**
consecutive samples per restart, forming a 1000×1000 matrix. §3.1.4.2: estimate row-wise and
column-wise; *"If the minimum of H_r and H_c is less than half of H_I, the validation fails, and
no entropy estimate is awarded";*
otherwise the assessment is `min(H_r, H_c, H_I)`. `ea_restart` requires exactly 1,000,000
samples.

For this device that is tractable, and the instrumentation is a smaller change than the
existing burst patch:

- **Storage is a non-issue.** Only 1000 bytes per restart are needed, out of the 691,200 a
  frame contains — 0.14% of one frame, 1 MB for the whole matrix. Keep the same 1000
  positions every time (column *j* must mean the same photosite across all restarts), spread
  across the frame rather than clustered, and do not move the device.
- **Wall clock is the cost.** The rig's documented timings (10 s quiet period, ~0.59 s between
  burst frames) put one capture cycle in the tens of seconds, so 1000 of them is an overnight
  run rather than an infeasible one. Setting `BURST_N = 1` removes most of the per-cycle
  burst time, since only the final frame is needed.
- **Whether a "restart" means a fresh capture or a fresh boot is a judgement call** that must
  be recorded. The strict reading is a power cycle, which adds Pi Zero boot time per restart.

**Why this is the piece worth building, and the sequential estimators are not.** The non-IID
suite has short memory: MultiMMC and LZ78Y look back 16 samples, Lag 128, MultiMCW at most
4095 (verified in the tool source: `D_MMC 16`, `B_len 16`, `D_LAG 128`, `W = {63, 255, 1023,
4095}`). A frame is 691,200 samples. Concatenating two successive photographs of the same
scene into one 1,000,000-sample stream confirms this — the estimate barely moves (bookshelf
0.5458 → 0.5667; wall 0.9243 → 0.9448), because **no sequential estimator can see a repeat at
691,200-sample lag.** Long-range reproducibility is invisible to them by construction. The
restart test's column direction is the only part of 90B that looks for it, and it is exactly
the check that would catch the failure mode this analysis already identified by other means:
a light-starved sensor returning the same near-constant frame on every attempt.

## What 90B asks for that we do not have

90B is a validation regime for a *designed* entropy source, not a score you compute from
data. Its §6 preamble says so directly: the estimators *"should not replace in-depth analysis
of noise sources, but should be used to support the initial entropy estimate of the
submitter."* And H_I includes H_submitter in its minimum — **the standard will not award more
entropy than the designer claims.**

Against SeedSigner v0.8.7 the structural gaps, none of which any estimator run can close:

- **§3.2.2 #1** — documented noise-source description: *"how the noise source works, where the
  unpredictability comes from."* The analysis now supplies this (photon shot noise); the
  project does not.
- **§3.2.2 #2** — stationarity, a **shall**. A camera whose distribution moves with lighting,
  exposure and scene is in tension with it on its face. This is the honest structural
  objection to camera entropy under 90B, and it is worth stating plainly rather than
  defending against.
- **§4.3/§4.4** — health tests: *"shall include both continuous and start-up tests,"*
  performed *"on the noise source samples before any conditioning is done."* The two approved
  continuous tests are the **Repetition Count Test** (§4.4.1) and the **Adaptive Proportion
  Test** (§4.4.2). **v0.8.7 has neither.** A Repetition Count Test is precisely what would
  catch the all-zero preview window and the preview-zero state this analysis measured — and
  it is a cheap device-side check, which makes it the one directly actionable item here for
  the upstream entropy-hardening campaign.
- **§3.2.4 #2** — validation data *"shall be raw output values"*, with a dedicated raw-sample
  interface (§3.2.1 #5). The capture rig is effectively that interface; stock firmware has no
  such path.

On the conditioning question, which readers also raise: SHA-256 is a **vetted** conditioning
component (§3.1.5.1.1), and for vetted components the estimators are *not* run on the output
at all — entropy is computed by closed formula from `h_in`, the validated **raw** assessment.
*"Since the conditioning component is deterministic, the entropy of the output is at most
h_in."* **There is no path in 90B by which testing hashed output produces an entropy credit.**

## The BSI contrast, if a reader raises AIS 31

Where 90B says a stochastic model *"may"* be provided (§3.2.2 #3), BSI's AIS 31 makes it
mandatory for physical RNG classes PTG.2/PTG.3 — *"A stochastic model is the core of
evaluating PTRNGs according to the AIS 31."* Its critique of pure black-box testing is
unusually quotable and applies exactly to the reader intuition this document rebuts:

> "Black box tests, meaning that they are not tailored to the design of the noise source,
> will perceive all information in their input as random. … Therefore, a black box
> statistical evaluation of a noise source without considering its nature is prone to
> overestimating the quality of a TRNG."

([BSI, *A Proposal for Functionality Classes for Random Number Generators* v3.0, Sept 2024](https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Certification/Interpretations/AIS_31_Functionality_classes_for_random_number_generators_e_2024.pdf))

That is the whole argument in one sentence, from a standards body: a rich-looking scene
*looks* like entropy to a black-box test. Which is why the published analysis measures what
changes between captures rather than what a single photograph contains.

## Reproducing this

```bash
git clone --depth 1 https://github.com/usnistgov/SP800-90B_EntropyAssessment.git
# deps per the repo's own dockerfile: g++ libbz2-dev libdivsufsort-dev libjsoncpp-dev
#                                     libgmp-dev libmpfr-dev libssl-dev make
cd SP800-90B_EntropyAssessment/cpp && make iid non_iid restart
```

Dataset construction (from `image-entropy/dataN/`, run at the repo root):

```python
import numpy as np, pathlib
d = pathlib.Path("image-entropy/data5/burst-19700101-000306-6b66/stock")
M = np.stack([np.fromfile(f, dtype=np.uint8) for f in sorted(d.glob("frame*.raw"))])

# difference domain, mod 256, five disjoint pairs -> 1,000,000 samples
diff = np.concatenate([((M[i+1].astype(np.int16) - M[i].astype(np.int16)) % 256)
                       .astype(np.uint8) for i in (0, 2, 4, 6, 8)])[:1_000_000]
diff.tofile("whitewall_diff.bin")

# column-major (restart-test shape, r=10): one photosite down all captures, then the next
pos = np.arange(0, M.shape[1], M.shape[1] // 100_000)[:100_000]
M[:, pos].T.reshape(-1)[:1_000_000].tofile("whitewall_col.bin")

# brightness bands (data1/000303): partition by the ten-capture mean level, then an
# evenly spaced 100,000-position subsample of the band, column-major. This EXACT
# construction is load-bearing: an adversarial recomputation (2026-08-09) showed the
# band floors swing from ~0.02 to ~2.48 bits/sample across otherwise-plausible readings
# of "partition and subsample" (truncate-first, all-samples, capture-major, ...), and
# one reading inverts the whole-frame-below-both-bands ordering. The figures quoted in
# Result 4 (bright 2.3455, dark 0.2102, whole frame 0.0895) come from this code and
# should not be cited without it.
lvl = M.mean(0)
for name, mask in [("bright", (lvl >= 100) & (lvl <= 200)), ("dark", lvl < 40)]:
    sel = np.where(mask)[0]
    pos = sel[np.linspace(0, len(sel) - 1, 100_000).astype(int)]
    M[:, pos].T.reshape(-1)[:1_000_000].tofile(f"bookshelf_col_{name}.bin")
```

```
./ea_iid     -i -a whitewall_diff.bin 8
./ea_non_iid -i -a whitewall_diff.bin 8
```

`ea_iid` takes tens of minutes on 1,000,000 8-bit samples (10,000 permutations);
`ea_non_iid` runs in a couple of minutes.

## If any of this reaches a published page

It is new measurement, so it is a §15 corrections entry and a claim-ID assignment, not a
silent edit — and IE-L-01's wording ("no full NIST SP 800-90B assessment... unquantified
amount") becomes stale the moment Result 3 is published. House custom suggests an adversarial
review round for a change of this size. `CONVENTIONS.md` governs; re-read it rather than
trusting this paragraph.
