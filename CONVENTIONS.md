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
the strong form**, and is preferred once part two is large enough to have its own audience.

**Where a document is a reference rather than an analysis, the light form is a trailing appendix.**
`dice/standard.html` is the worked example: the reader-facing guide runs to the part break, and
everything a checker needs (per-source measurement detail, pinned source tables, the method for
adding a row) sits behind it. Send fine-grained detail there by default. A statistic a human cannot
act on, a caveat about a study's sampling, a chi-square, a p-value: all of it goes to the appendix
with a link, not into the paragraph. The reader-facing half states the finding and moves on. When
they are separate documents, each states plainly which reader it is for, and part one links to
part two wherever it relaxes a claim rather than dropping the rigor.

### Three tiers, once a reference outgrows two

`dice/standard.html` is the worked example. A catalog that covers many implementations splits into
three, and the split is by **who is reading and why**, not by subject:

1. **The narrative.** Read start to finish, by a human deciding what to do. Ruthlessly efficient.
   Its enemy is detail: too much of it, detail that does not change what the reader does, or detail
   that is covered properly elsewhere. Human attention does not survive being handed every caveat
   at once, and the cover-your-ass material has a home further down the page.
2. **The reference.** Jumped into, never read in order, by a human looking up the one entry that
   matches their tool. Straightforward, mechanical, explanatory. **No cross-references between
   entries**: a reader who lands on one has not read the others and does not care about them.
   Anything an entry needs, it states.
3. **The appendix.** Almost no human reads it. Its consumer is a model checking a claim, so it
   carries the vectors, the constructions, the pinned sources and the reproduction steps.

**A tier-1 argument cannot rest on a distinction the reader does not already hold.** That a Bitcoin
key is worth about 128 bits however much entropy went into the seed is true, sourced and
interesting, and it came straight back out of the narrative: making it land requires holding *seed*
and *key* apart, and to most people outside the subject those words are interchangeable. An
argument that has to teach a distinction before it can be made is an appendix argument, however
good it is. Reference it in passing where it is directly relevant, or leave it alone.

The failure mode this exists to prevent is detail migrating **up**. A caveat that belongs in tier 3
lands in tier 1 because it felt important while writing, and the narrative slowly becomes the
appendix. When trimming tier 1, the question is not "is this true or useful" but "does a human
deciding what to do need it *here*". If the answer is no, it moves down rather than out.

The contents should show the tiers, named and nothing more. A label the reader already understands
does the work: *Appendix* lands where an in-house coinage like *The working* does not. Do not
annotate the labels with reading instructions. A note under *The guide* telling someone to read it
in order is telling them to do what they were going to do anyway, and it costs the label its
authority.

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
2. **The short version** — a verdict line, then the headline claims that support it, scannable in
   isolation. A numeric grid (`.sgrid`) is the alternative where a subject really is best summarized
   by figures.
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
- **A paraphrase is not a quote, and the qualifiers are where the meaning lives.** An early draft
  summarized the Coldcard disclosure's exception as "50 or more fair dice rolls." The source says
  "at least 50 fair, independent and private rolls": two dropped words, each carrying a condition
  the reader has to meet, and both of them things this page argues for elsewhere. Where a source's
  exact wording is load-bearing, quote it rather than compressing it, and **check the quote against
  the raw page** rather than against a fetched summary, since a tool that renders a page through a
  small model returns text that reads verbatim without promising to be.
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
- **Re-run the shipped scripts before publishing, and reconcile every figure against their
  output.** A number drafted into prose and a number a shipped script prints drift apart silently:
  a seed changes, a script is rewritten, a scenario is renamed, and the page keeps quoting the old
  result. The dice page had three such figures, all close enough to look right and all wrong
  against the script a reader is invited to run. The script is the artifact anyone can execute, so
  the script wins; where they disagree, fix the page.
- **Do not inflate.** "This is fine, and here is the code that makes it fine" is as valuable as
  a finding.
- **A summary headline must be the strongest claim the body actually supports, and no stronger.**
  Compressing for impact is where overclaims enter. "More rolls are not safer" reads well, but the
  section it summarized concedes that extra rolls do restore what a biased die costs; "the math says
  more rolls are not necessary" is the claim that survives its own section. Where the point is to
  answer a superstition, clinical and exact beats emphatic: the reader arguing with you will check.

## Method notes that recur

**Never evaluate seed quality with statistical randomness tests.** Every SeedSigner entropy path
ends in SHA-256, whose output is statistically perfect regardless of input. Output-side testing
is guaranteed reassuring and guaranteed uninformative. Assess the source instead.

**Confront the misconception directly.** Correcting folklore is a large part of what these
documents are for, and it has to stay front of mind: roll more for safety, buy casino dice, test
your dice, verify your real seed somewhere else. Name the belief and refute it in the same breath.
Do not open a section by restating the folklore and leave the correction for the fourth paragraph,
because a skimmer reads the heading and the first line, and those are where the belief is confirmed
or broken.

**A myth-dispelling document leads with the reassurance, not a replacement worry.** Where the
subject is over-complicated by folklore, the verdict line says the thing is easier than its
reputation and the reader can get on with it. Promoting the one real caveat to the headline
("the dice are not the part to get right, how they tumble is") swaps one anxiety for another and
reads as though the page has found something new to fear. The caveat belongs in the bullets, where
it is a technique note rather than a warning.

The harm is usually social rather than technical. Someone convinced that 120 rolls are necessary
tells everyone who rolled 99 that their seed is deficient, and that doubt spreads faster than the
correction, landing on people who did nothing wrong. Say so where it applies.

**The same trap catches the page's own advice.** A recommendation phrased as protection implies
the alternative is exposed: "if you're worried, choose 24 words" tells every 12-word holder they
are short of some margin, which is the identical superstition one length up. Check each
recommendation for what it implies about the option not taken.

The correction is not to rank them the other way. Declaring the larger option no safer is its own
overclaim, and 12 against 24 words is a genuine gray area rather than a settled one. What survives
is a comparison of magnitudes instead of a verdict on either: *choosing 12 or 24 words has a bigger
impact on your backup strategy than on your security.* That concedes the security dimension exists,
declines to adjudicate a question a bullet cannot settle, and still hands the reader the criterion
that decides it in practice. It is also why the
refutation must be exactly as strong as the evidence and no stronger: a reader who is arguing with
the page will check, and one overclaim discredits the correct claims beside it.

**An honest concession must not turn into a how-to for the thing you are arguing against.** The
dice page concedes that extra rolls do offset a biased die, because they do. An earlier draft then
tabulated how many extra rolls each level of bias needs to reach a full 256 bits, which reads as
instructions for compensating and quietly grants that compensating is the move. It is not: a die
skewed enough to matter is a die to replace. Where the real remedy differs in kind from the folk
remedy, name it rather than costing out the folk one. Concede in a clause, and spend the paragraph
on what to actually do.

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
- **Commas.** The Oxford comma is required in any series of three or more. The comma before "and"
  or "or" joining just two elements is optional, and is omitted unless it genuinely aids clarity.
  Where dropping it would garden-path the reader ("costs you bits and fewer bits means"), split the
  sentence rather than reinstate the comma.

### Social cards

Each document declares an `og:image`. `dice/figures/` is the worked example, and its README carries
the render command.

- **Render the card from the document's own stylesheet** rather than drawing one. It then cannot
  drift from the page's type or palette, and both themes come from a single source file.
- **Whatever the card asserts has to be true.** The dice card shows the §8 worked example, and its
  digest recomputes from the roll string on the page. A card is the most-shared artifact a document
  has and the least likely to be checked, which is exactly why it does not get invented content.
- **Nothing on a card is set below 19px.** X shows a 1200px-wide card at roughly a third of its
  size, where 13px type lands at about 4px. That is not small text, it is noise: unreadable at every
  size the card actually appears, while still costing contrast. If a line is not worth 19px, cut it
  rather than shrink it. One deliberate exception is allowed where something stands for its kind
  rather than asking to be read, as the digest does.
- **Check edits at ~400px wide**, not at full size. Dark grounds read better at that scale than the
  page's paper default, so the shipped card and the document's default theme need not match.

### Cutting

Established across the dice restructure, where roughly a third of the drafted prose was removed
without losing a claim. Each of these shipped at least once before being caught.

- **Do not restate what a chart or table already shows.** If a bar is labeled 253.1 next to a fair
  row labeled 255.9, a pull-out box computing "2.9 bits" is subtraction the reader already did.
  Prefer deleting the box to trimming it.
- **Do not preview a point you make a paragraph later.** Cross-references earn their place across
  sections, not across adjacent paragraphs.
- **A summary states its claims; it cannot prove them, so stop trying.** The short version carries
  headline claims and a link to the section that establishes each one. A figure dragged up into a
  bullet ("under 3 bits of 256") or a justifying clause ("a seed holds a fixed number of bits, so
  extra rolls are discarded") is evidence doing evidence's job in the wrong place. Summary bullets
  are scanned rather than read, so cut to the claim: a lead-in that only sets up the point
  ("Don't take that on trust:") is the first thing to go.
- **Frame the positive claim positively.** "Buying better dice does not buy a better seed" beats
  "cheap dice cost you under 3 bits", which states a reassuring finding in the grammar of a
  penalty. Same fact, opposite impression.
- **Positive framing must not flatten into a false equivalence.** "Cheap dice do the job as well as
  casino-grade dice" reads well and is not true in general: precision dice are measurably fairer,
  and a reader who knows that dismisses the whole document over one bullet. The claim that survives
  is the scoped one, conceding the difference and denying its magnitude: "casino dice are provably
  fairer, but would have essentially no impact on your seed." A hedge like *essentially* carries
  real weight in a sentence like that, and it earns its place because the summary links to the
  figures rather than asserting the point alone. Any summary claiming two things are equally good
  should be checked for the domain it is silently assuming.
- **Guidance carries only the precision the reader can act on.** "Give every roll plenty of tumble"
  is the instruction; which conditions make the follow-through matter belongs in the body, where
  the mechanism is explained.
- **Put the reader-facing conclusion first, then the concession.** "Casino dice do not matter here.
  They are provably better, but not in a way that changes your entropy" beats the same facts in the
  reverse order, which reads as advocacy for the thing you are dismissing.
- **A pull-out box's title must be set at least as large as the body that answers it.** These
  titles are not labels, they are the sentence the first line replies to: "What the box is for" /
  "Speed.", "Does a 256-bit seed buy 256 bits of security?" / "No." The shared `.note .tag` sets
  them at 0.61rem against a 1rem body, so the eye skips the title and the opening line arrives with
  nothing to attach to, which reads as incoherence rather than as a missed label.
  `dice/standard.html` overrides `.note .tag` to 1.05rem, sentence case, keeping the warn and pass
  colors. Treating this as a per-box opt-in was the earlier mistake: the pattern is how these boxes
  are written, so the fix belongs on every one of them.
- **Quantify invented scenarios in the units of the real measurement** they will be compared
  against. Qualitative tiers ("very good" to "bad") hid a calibration error for three drafts.
- **Do not write fractions humans do not process.** "0.2 bits", not "a fifth of a bit".
- **Say the plain thing rather than announcing that you are saying it.** A section retitled
  "Detecting bad rolls" does not also need a sentence explaining that it is not a technique tip.
- **Fixing an overcorrection is not a licence for a new one.** Several rounds here replaced buried
  prose with an equally long correction of it; the answer was usually to delete.

## What does not belong in this repo

**Unfixed vulnerability details.** This repo is public. Analyses are published when their
findings are either benign or fixed. Work covering live defects stays in a private working
directory until disclosure is resolved.
