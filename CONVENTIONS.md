# Series conventions

Every analysis in this repo follows the same **evidentiary rules**. Structure is looser and still
settling: the series is early and deliberately ad hoc, so what follows records what has worked
rather than what is required. This document is the shared reference, so each analysis carries only
what is specific to its subject.

## What these documents are

AI-assisted analyses of SeedSigner subsystems, produced by SeedSigner's lead developer. **Not
independent audits, and not official project publications.** No engagement, no auditor liability, no certification. The value is that every claim
is pinned to a source line or a measurement, and every document says what it could not verify.

Naming: *analysis*, not *audit*. The distinction matters and should not erode.

## Two parts, two audiences

The one structural rule worth holding to. Everything under "Document structure" below is a
skeleton that has worked so far, not a specification; these analyses are still ad hoc and the
shape should follow the subject.

Once an analysis outgrows a few thousand words, split it in two:

- **Part one, the analysis.** What the subsystem does, what was found, and what the reader has to
  do about it. Written for a person deciding how to use the device. It should carry everything a
  non-specialist needs, and it should end *before* the measurement detail starts.
- **Part two, the data and methodology.** How the measurements were taken, what they returned, the
  release history, the adjudication record, the limitations, the reproduction instructions. Written
  to be checked rather than read: declarative, dense, claim-first. Increasingly this is the half an
  AI reviewer actually consumes.

The split exists because reader-facing material was being buried behind measurement sections that
most humans never reach. Anything a user needs in order to use the device safely belongs in part
one, however technically interesting the evidence for it is. The converse also holds: material a
user cannot act on does **not** belong in part one merely because it is interesting, and moving it
out is not hiding it when part two is published alongside.

**A visible part break inside one document is the light form. A full break into two documents is
the strong form**, and is preferred once part two is large enough to have its own audience. When
they are separate documents, each states plainly which reader it is for, and part one links to
part two wherever it relaxes a claim rather than dropping the rigor.

**Part two is presented AI-first**, and says so. Its primary consumer arrives to check claims
rather than to learn, so it opens with a **reviewer brief**: precedence when sources disagree,
which estimators are in play and what they bound, how to report a finding, and the settled false
positives that should not be re-filed. State the approach explicitly, and give a prompt that can be
copied without reading the document first.

**Describe the structure, do not warn readers off.** AI-first is a statement about how part two is
organized, not a barrier to entry. Say that pointing a model at it is the fastest way to get a
claim checked; do not say it is not for reading, and do not editorialize about how tedious it is.
An interested human should finish that paragraph feeling invited, with a route in (the claim
ledger) rather than discouraged.

Style density is a cue for human readers only. A machine takes its structure from the
markup, so the work that makes part two machine-readable is **stable claim IDs**, canonical tables,
stable anchors and explicit status labels, not type size.

Part one relaxes, it does not weaken. Where part one drops an estimator taxonomy or a hedge, it
still quotes the conservative figure and points at the document that carries the full reasoning.

## Document structure

A common skeleton, not a specification.

1. **Masthead** — title, one-sentence standfirst, meta strip (reviewed version, history span, key count, model)
2. **The short version** — four figures, scannable in isolation
3. **Contents**
4. **The implementation** — what the code does at the reviewed tag, with pinned source links
5. **Verification** — *traced, not just read*; what was measured and how
6. **Results**
7. **Every release, checked** — per-release history table, and the direct answer to "was it ever weaker?"
8. **Degenerate cases** — subject-specific failure modes and their reachability
9. **Adjudication record** — every concern raised, its disposition, and where that disposition is weakest
10. **What we did not verify** — limitations, stated plainly
11. **How to check this yourself** — reproduction instructions, plus AI-reviewer guidance
12. **Scope and provenance** — versions, models, correction history

## Evidentiary rules

- **Label claims VERIFIED or INFERRED.** Verified means read from source at a pinned commit, or
  measured. Inferred means reasoned, with the inference stated.
- **Pin every source link to a tag**, never a branch, so line numbers stay correct.
- **Pin every layer of the measured stack, not just the one being edited.** A measurement
  claiming to characterize a released version must be built from refs traceable to that
  release at *every* layer — app, OS, firmware — with each pinned ref recorded alongside the
  data. Pinning the layer you happen to be modifying while taking another from whatever
  branch was convenient yields a result that characterizes nothing shipped, and nothing in
  the data shows it. Verify against the **upstream** remote specifically: a fork can carry
  the release tag's name without the release's contents. Enforced by the provenance gate in
  `image-entropy/capture-rig/build-instrumented-image.sh`, which refuses to build from a ref
  it cannot trace upstream and stamps any override into the provenance record.
- **Publish corrections made after publication.** Once a document is public, a substantive
  change is recorded in it — what changed and why — rather than silently applied. Pre-publication
  drafting is not a correction history and should not be presented as one. Each document's
  masthead carries an **Updated** date linking to its corrections record; bump it in the same
  edit as the corrections entry, so a reader who remembers different figures can date the
  change. Body prose otherwise states the current analysis without narrating its own history.
- **State the weakest point** of each disposition. A reviewer should be able to find the soft
  spots without re-deriving the whole analysis.
- **Ship the raw data.** Measurements include the inputs they were computed from, so a
  disagreement can be settled numerically.
- **Do not inflate.** "This is fine, and here is the code that makes it fine" is as valuable as
  a finding.

## Method notes that recur

**Never evaluate seed quality with statistical randomness tests.** Every SeedSigner entropy path
ends in SHA-256, whose output is statistically perfect regardless of input. Output-side testing
is guaranteed reassuring and guaranteed uninformative. Assess the source instead.

**Adversarial verification.** Significant findings go to a fresh agent instructed to *refute*
them, defaulting to "refuted" when uncertain. False positives cost real time and discredit the
findings around them.

**Prediction before measurement.** Where a source reading implies a measurable outcome, record
the prediction first. Agreement then means something.

## Deployment reality

Applies to every analysis. Candidate findings that depend on these do not apply:

- **No wireless hardware.** Not disabled — absent from the reference hardware.
- **Runs entirely in RAM.** Root filesystem is an initramfs image; no persistent filesystem.
- **Physical access is outside the threat model.**
- **Malicious microSD cards are outside the threat model.**
- **The absence of a hardware RNG in seed generation is deliberate.** SeedSigner uses only
  external, user-supplied entropy — dice, coin flips, camera. Recommending `os.urandom` or TRNG
  mixing is a design debate, not a vulnerability report.
- **The human observer is a real security control.** Where a flow requires the user to watch a
  live preview and accept a reviewed capture, that verification is performed by a person by
  design. An AI reading only the code will flag its absence as critical; that is a false
  positive.

## Presentation

- Shared assets in `assets/` — `fonts.css` (SS Sans / SS Mono) and `series.css`. Documents link
  to them rather than inlining, so they cache across the series.
- Each analysis is a standalone `index.html` in its own directory, with `figures/`, `evidence/`
  and any raw `data/` alongside.
- Color is semantic: the accent is structural only (rules, eyebrows, section numbers), green
  carries "verified", amber carries "caveat". Never put the accent on a status element.
- Figures state their processing parameters — gain, crop, scaling — so they can be regenerated.
- **Short paragraphs, one point each**, especially in part one. A paragraph that makes three
  points is three paragraphs. Break rather than pack.
- **American spellings** throughout: color, behavior, favoring, labeled, modeling, analyze,
  -ize rather than -ise. The exception is quoted material: source code, code comments, and
  direct quotations keep whatever spelling the original used.
- **No em-dashes in body prose.** Use commas, colons, or parentheses. (Page `<title>` and
  `<meta description>` are exempt.)

## What does not belong in this repo

**Unfixed vulnerability details.** This repo is public. Analyses are published when their
findings are either benign or fixed. Work covering live defects stays in a private working
directory until disclosure is resolved.
