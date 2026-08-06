# Verifying other people's wallets: four ways the check quietly proves nothing

Established 2026-08-05 during the adversarial review of the `dice/` analysis pair. Every item
below is a mistake that was actually made and shipped into a draft, then caught only because a
second agent was told to refute rather than confirm. They are recorded because the same traps
recur on any survey of third-party implementations.

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

---

## The meta-lesson

All four survived a first review pass and were caught only by agents briefed to *refute*, with an
instruction to default to "refuted" when uncertain. A pass briefed to check correctness confirms;
a pass briefed to break things finds these. See also the reverse failure: in the same review, two
agents disagreed about a figure and the one recommending a "fix" was wrong — the shipped script
was the buggy artifact and the published number was right. Verify agent findings before acting on
them, in both directions.
