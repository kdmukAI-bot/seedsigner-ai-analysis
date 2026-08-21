# Verifying other people's wallets: eight ways the check quietly proves nothing

Established 2026-08-05 during the adversarial review of the `dice/` analysis pair. Every item
below is a mistake that was actually made and shipped into a draft, then caught only because a
second agent was told to refute rather than confirm. They are recorded because the same traps
recur on any survey of third-party implementations.

Items 7 and 8 were added 2026-08-20. Both had already reached the published page, so they are
recorded in `dice/standard.html` §21 as corrections as well as here.

Backing evidence for the dice survey itself lives in `dice/evidence/wallet-dice-survey.md`.

---

## 1. A cross-check between two transcriptions of the same function is an identity test

The published headline was "**0 mismatches over 4,000 sequences run against Coldcard**." The
script compares:

```python
# "Coldcard"                          # "SeedSigner"
md = hashlib.sha256(b"")              entropy = hashlib.sha256(rolls.encode()).digest()
for ch in rolls: md.update(ch)
seed = md.digest()
```

Streaming and one-shot SHA-256 are the same function by definition. The comparison **cannot
produce a mismatch for any input**, so neither the 4,000 nor the 0 carries information. Running
it more times does not help; the number is decorative.

Two compounding problems:

- Nothing of Coldcard's was executed. Its construction was *transcribed* from source into Python
  by the same process that had just read SeedSigner's version, which is exactly where a shared
  misreading survives.
- The figure was filed under "Executed" and presented as a stronger evidence class than the
  source reads, when it is weaker than either.

**Rule:** before reporting a cross-implementation agreement figure, ask what input would make it
disagree. If you cannot construct one, you have measured nothing. Genuine independence requires
either running the other project's own code, or a reimplementation written from the specification
by someone who has not read the first one.

## 2. The affordance is not always where the entropy is

Sparrow was classified "no dice support" after reading its seed-*generation* path, finding
`SecureRandom.getInstanceStrong()`, and stopping. That verdict was wrong. Sparrow ships a genuine
checksum-solving last-word calculator — `Bip39MnemonicCode.getPossibleLastWords()` — wired into
the seed-*entry* UI at `MnemonicKeystorePane`, plus a Border Wallets grid flow that feeds it.
Present since release 1.7.4 (2023-04-04).

A last-word calculator is a *reading* feature, not a *generating* feature. It will never appear in
the code path that creates a seed, because it exists for seeds created elsewhere.

**Rule:** for any "can I bring my own entropy" question, read the entry/import path as well as the
generation path. They are different code and often different files.

## 3. Documentation-only affordances, and documentation that lies by omission

- BitBox02, Jade and Passport ship features built for hand-rolled seeds while their firmware
  contains no dice arithmetic at all. Grepping firmware for dice misclassifies all three. Two of
  the three publish dice procedures as PDFs on their own help sites.
- The inverse also happens. Sparrow's own docs describe *neither* of its two relevant features,
  and mention dice only to tell you to mix rolls into a Coldcard. Absence from the docs is not
  absence from the product.
- Blockstream Jade's lookup table 404s on `help.blockstream.com` but resolves on the
  `blockstream.zendesk.com` alias. A dead vendor link is often a broken host alias, not a
  withdrawn document. Check the alias before recording something as unverifiable.

## 4. Naming a category by its mechanism instead of its absence

The "No dice" group was introduced as *"These generate seeds from their own random number
generator, and offer nothing for dice beyond the ordinary ability to type in a phrase."* Both
halves are false for members of the group:

- **Satochip** has no seed-generation command at all. The applet exposes only
  `INS_BIP32_IMPORT_SEED`; the seed is generated on the *host* by `python-mnemonic` and pushed in.
- **Ballet** is BIP38 with both key halves factory-generated. No mnemonic exists.
- **NGRAVE ZERO** documents real user entropy: fingerprint images, ambient light via camera, and a
  freeze/shuffle step. It is not dice and not user-*determining* (shuffling re-randomizes from
  device entropy; the user only chooses when to stop), but it is not "nothing," and at least one
  widely-cited comparison table already scores it "User Added Entropy: YES."

**Rule:** define a negative category by what it lacks, not by a mechanism you assume all its
members share. The verdict can be right while the stated rationale is refutable, and the rationale
is what a knowledgeable reader attacks.

## 5. A one-label-per-implementation taxonomy hides capabilities that cut across classes

Added 2026-08-11. The survey classified each implementation into exactly one of four classes by
*which construction it applies to your rolls*: (a) hash the ASCII rolls, (b) some other dice
arithmetic, (c) no dice arithmetic, the device only solves the checksum-valid final word, (d)
nothing.

Class (c) was described as though the final-word calculator were its defining feature. It is not.
Checking the seed-entry path on the class (a) devices found that **all four of them also complete a
hand-built phrase**:

| Implementation | Where |
|---|---|
| SeedSigner | `ToolsCalcFinalWord*` in `views/tools_views.py` — a dedicated tool, coin flips / a word you pick / zeros |
| Coldcard | `WordNestMenu` in `shared/seed.py`, offers only `bip39.a2b_words_guess(words)` on the last word |
| Krux | `Key.get_final_word_candidates()` in `pages/mnemonic_editor.py` |
| Kern | `manual_input_page_create(..., checksum_filter_last_word=true)` from the New Mnemonic flow |

So the paper-table method works on far more devices than the four vendors who document it. What
actually separates BitBox02 and Jade is not the capability but the **documentation**: they publish
the lookup table the method needs.

The fix was to stop assigning one label per implementation and publish a matrix instead:
implementations down, methods across, one mark per cell. Rows then carry more than one mark where
that is the truth (AirGap Vault implements two constructions; iancoleman.io implements three), and
a capability shared across classes becomes a column rather than a contradiction.

**Rule:** if any implementation legitimately belongs in two of your categories, the categories are
the wrong shape. Prefer a capability matrix, and keep a separate column for "the vendor documents
and supports this" when that differs from "the device permits it."

---

## 6. "Differs from canonical" is not a severity, and a membership check is not a position check

Surveying third-party dice worksheets (2026-08-16) meant verifying a *printed artifact* rather than
code. Five were checked against the BIP-39 wordlist and three carried cells that did not match it:
`TRUE` for `true`, `FALSE` for `false`, `March` and `October` for `march` and `october`.

Two things were wrong with how that was first reported, and both are general.

**The provenance explains the class of defect.** These are spreadsheet artifacts, not typos: a sheet
coerced `true` into a boolean and autocapitalized two month names. reardencode's README says
outright that its tables were built in Google Sheets. Any lookup table generated through a
spreadsheet is exposed to the same thing, so it is worth grepping generated artifacts for `TRUE`,
`FALSE` and capitalized month names specifically.

**But the severity was overstated, in three documents, before anyone checked what the deviation
actually does.** The canonical wordlist is lowercase, so `TRUE` is not a BIP-39 word at all.
Implementations reject it rather than deriving something different — verified against `embit`, which
raises `ValueError: Word 'True' is not in the dictionary`. The artifact cannot corrupt a seed
silently; it can only fail loudly, and in practice never even does that, because word entry on a
signing device goes through a lowercase keyboard with autocomplete.

The defect that *would* matter is the opposite shape: **a cell holding a real BIP-39 word that
belongs at a different index**. Nothing downstream questions it and it substitutes silently. None of
the surveyed tables had one.

The lesson: when a comparison against a canonical list produces deviations, classify each by
failure mode *before* reporting it. "Does not match the reference" bundles a cosmetic artifact and a
silent-substitution risk into one alarming sentence, and the write-up inherits an urgency the
evidence does not support.

**Related trap, same survey.** Four tables were verified *positionally* (every index compared to the
word it claims) and one only for *membership* (all 2048 words present, plus outcome-count
arithmetic), because its two-page print layout defeats reliable text extraction. A membership check
cannot catch a transposition inside a row, which is exactly the silent defect above. State the depth
of check per artifact; a single "verified against the wordlist" claim over a set that was checked to
two different depths is the kind of blanket assurance this document exists to prevent.

## 7. A function with no caller is not a feature

`dice/standard.html` §7 recorded SeedSigner as accepting coin flips as well as dice, and the survey
justified the mark by citing `helpers/mnemonic_generation.py`
`generate_mnemonic_from_coin_flips`, which takes 128 or 256 binary characters, hashes them, and is a
correct implementation of the reference construction over a binary alphabet.

The function has **no caller anywhere in `src/` or `tests/`** at tag `0.8.7`. No menu reaches it.
The live coin-flip affordance is the Calc Final Word tool, which supplies only the last word's spare
bits and goes through `get_partial_final_word`, a different function.

The survey found the code by searching for the construction and stopped there. Finding an
implementation proves the *code* can do it; it says nothing about whether the *product* does. For a
chart that answers "what can I do on this device," reachability is the claim, and reachability means
tracing back to a view, a menu entry, or a documented flow.

Cheap check, worth running on every capability claim:

```bash
git grep -n "<function_name>" <tag> -- 'src/*' 'tests/*'
```

One hit, the definition itself, is the tell. Related to pitfall 3, which is about documentation
overstating code; this is code overstating the product, and it is easier to fall for because
reading the source feels like the rigorous move.

## 8. A claim verified at a pinned commit can expire before it is published

`dice/standard.html` §13 listed Passport Prime among wallets offering nothing for dice. That was
read from source and correct at KeyOS `v1.3.0` (`425c9791`), the commit the survey pinned.

KeyOS `v1.3.1` shipped 2026-08-07 and added `random_last_word` in `utils/seed-quiz/src/lib.rs`,
wired into seed entry in two apps. The page was published 2026-08-16. The claim was therefore
**false for nine days before it went live**, and nothing in the process would have surfaced that:
pinning protects line numbers and reproducibility, not currency.

Pinning is still right. What it does not do is make a negative claim durable, and negative claims
are the exposed ones. "Implements X" stays true once shipped; "offers nothing" is one release away
from being wrong, and the vendor has no reason to tell you.

Two habits close the gap, both cheap:

- **Re-check negative claims against the latest tag immediately before publishing**, not against
  the pin. `git ls-remote --tags upstream` is one call and shows whether anything shipped since.
- **Verify the change is real before recording it as one.** Here, `git ls-tree -r v1.3.0` returned
  no path under `utils/seed-quiz`, confirming a new feature rather than a missed read. That
  distinction decides whether the correction reads "we were wrong" or "this changed," and they are
  different statements about the analysis's reliability.

## The meta-lesson

All four survived a first review pass and were caught only by agents briefed to *refute*, with an
instruction to default to "refuted" when uncertain. A pass briefed to check correctness confirms;
a pass briefed to break things finds these. See also the reverse failure: in the same review, two
agents disagreed about a figure and the one recommending a "fix" was wrong — the shipped script
was the buggy artifact and the published number was right. Verify agent findings before acting on
them, in both directions.

**Items 7 and 8 were caught by neither mechanism.** Both were found by the project's own developer
reading the finished draft and saying "that isn't how that works" — one about a device he maintains,
one about a vendor he tracks. Adversarial agents did not catch them because both claims were
*internally* consistent: the code existed and had been read, the pin was real and correctly quoted.
Nothing in the artifact contradicted itself. That is the residual risk after every automated check
passes, and it is why a domain reader on the finished draft is not a formality.
