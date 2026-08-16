# Reading published measurements of physical randomizers

Established 2026-08-11 while grounding the `dice/` quality section in real research instead of
invented scenarios. Every item below changed a published figure or prevented a wrong one.

The subject is dice, but the traps are general: they apply to any attempt to turn someone else's
measurement of a physical entropy source into bits of seed strength.

---

## The sources, and what each one can actually see

Three studies carry the dice-fairness claims. They are not interchangeable, and the differences are
what make the combination trustworthy.

| Study | Design | What it can see |
|---|---|---|
| Labby 2009, *CHANCE* 22(4) | 12 cheap plastic dice, 315,672 rolls, per-face counts | Full per-face distribution. Convertible to min-entropy directly |
| Iversen, Longcor, Mosteller, Gilbert & Youtz 1971, *Psychometrika* 36(1) | 219 dice (58 cheap, 161 precision), 20,000 throws each, **odd/even only** | Per-die consistency across a real sample. No per-face figure |
| Kapitaniak et al. 2012, *Chaos* 22, 047504 | 3D dynamical model, validated against high-speed camera | Effect of throwing technique. Model, not a throw count |

**They are blind to each other's defect, and this is the important part.** Iversen's paper says so
itself: a bias where "the probabilities of opposite sides are equally inflated and other opposites
equally deflated, as they might be if the die were a rectangular parallelepiped instead of a cube"
cannot be detected by odd/even recording. That is exactly the defect Labby found with a micrometer
(the 1–6 axis running ~0.2% short, which lifts faces 1 and 6 together — one odd, one even, so it
cancels in the odd/even split).

They also disagree about the *cause*: Iversen attributes brand X's bias to pip weight (even faces
carry 12 pips to the odd faces' 9), while Labby tested that exact prediction on his dice and
rejected it at p = 0.00005. Both can be true of different manufacturing.

What survives both methods is the magnitude: worst face ~1.3% (Labby), even faces ~1.4%
(Iversen). Agreement across two encodings and four decades is worth more than either figure alone.

**Rule:** before combining measurements, work out which defects each design is structurally
incapable of seeing. Two studies agreeing is only meaningful if they could have disagreed.

## Do not convert a conditional probability into seed bits

Kapitaniak reports that a cubic die lands on the face that started lowest with probability **0.548**
when it lands without bouncing, and **0.199** on a hand throw with 4–5 bounces, against a fair
0.167. Those numbers are far larger than any manufacturing bias, and the obvious move is to run them
through the same `-log2(p_max)` conversion as everything else.

**That would be wrong.** The probability is *conditional on the starting orientation*. If the
starting orientation is itself uniformly random, the marginal distribution over faces stays uniform
and no entropy is lost at all:

    P(final = k) = Σ_j P(start = j) · P(final = k | start = j) = uniform, when P(start) is uniform

The loss appears only through **correlation between rolls**. If handling makes each starting
position a function of the previous result — picking the die up and setting it back the same way —
then successive rolls stop being independent, and it is independence, not the per-roll distribution,
that the `min(seed_bits, N · H)` arithmetic assumes.

The practical advice that follows is therefore about *handling* (let them tumble, scoop them up
carelessly, use a box) rather than about a bits penalty. No published measurement of how strong that
correlation is for real human rolling appears to exist; that gap is stated in the document rather
than papered over.

**Rule:** a probability quoted conditional on some state is not a distribution over outcomes. Check
whether the conditioning variable is known to the attacker before spending it as entropy loss.

## Label simulated scenarios by what they produce, not by adjectives

The dice-in-a-box simulation (`dice/dice_tendice_box.py`) generated four grades of dice from
gaussian per-face perturbations and labeled them "very good", "ordinary", "poor", "bad". Those
labels shipped in three drafts.

When the tiers were finally quantified, the *mildest* grade turned out to produce a worst face
**6.3%** above fair — three to five times worse than the 1.3–2% that had been measured on real
dice. The chart's entire scenario space excluded reality, and no reader or reviewer could have
noticed, because an adjective cannot be compared against a measurement.

Recalibrated to 2%, 6%, 13%, 26% (severities 0.015, 0.05, 0.10, 0.20), the top line became the
measured case and the chart started answering the question a reader actually has.

**Rule:** when a simulation invents its own severity levels, label each one with the quantity it
produces in the same units as the real-world measurement you will compare it against. Adjectives
hide calibration errors indefinitely.

## Getting at the sources

- **Iversen 1971 is paywalled at Springer and Cambridge, but reprinted in full** in *Selected Papers
  of Frederick Mosteller* (chapter 23), which is findable as a complete HTML/PDF scan. The reprint
  carries the full text including the apparatus description, the per-brand block counts and the
  odd/even blindness caveat. This saved the entire finding; the abstract alone gives none of it.
- **Springer PDF links redirect to an auth host** and fail. Fetch the reprint or a mirror instead.
- **WebFetch on a PDF stores it locally**; the path is in the tool result and `pdftotext -layout`
  on that file works when the fetch tool itself returns only binary noise. This is how both the
  Labby and Kapitaniak papers were read.
- **YouTube captions are not retrievable** without a token (the `timedtext` endpoint returns 200 and
  zero bytes in every format). Video metadata — title, channel, upload date, description, chapter
  list — *is* available from the watch page HTML and the oEmbed endpoint, which is enough to cite a
  video's claims as attributed rather than verified.
- **Reddit is unreachable** from this environment: the JSON API returns 403, and reddit.com is
  blocked for the search crawler, so a user's recollection of a Reddit thread cannot be checked
  here. Ask for the link.
