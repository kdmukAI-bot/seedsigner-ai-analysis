# Dice and coin-flip entropy — the "all fives 99 times" question

Analysed by the coordinating session against tag 0.8.7.

## The design is correct (VERIFIED)

`helpers/mnemonic_generation.py` hashes the roll string with SHA-256 and takes 16 or 32
bytes. Roll counts are `DICE__NUM_ROLLS__12WORD = 50` and `DICE__NUM_ROLLS__24WORD = 99`:

| Rolls | Entropy of a fair d6 sequence | Target |
|---|---|---|
| 50 | 129.2 bits | 128 |
| 99 | 255.9 bits | 256 |

Correctly sized, with the margin in the right direction.

**Early exit is genuinely prevented (VERIFIED).** `ToolsDiceEntropyEntryView` passes
`return_after_n_chars=self.total_rolls` to the entry screen (`views/tools_views.py`), so
the flow returns only once exactly the required number of rolls has been entered. The
maintainer's understanding here is confirmed in code, not merely assumed.

## The gap, quantified — and it is narrower than it looks

No check rejects a degenerate roll sequence. Keyspace for a 99-roll entry using only
`k` distinct faces:

| Distinct faces used | Keyspace | Brute-forceable? |
|---|---|---|
| 1 (e.g. all fives) | 0 bits — 6 candidates total | **Yes, trivially** |
| 2 | 99.0 bits | No |
| 3 | 156.9 bits | No |
| 4 | 198.0 bits | No |
| 5 | 229.9 bits | No |
| 6 | 255.9 bits | No |

So low *diversity* is mostly harmless. A user who only ever rolls two faces still has 99
bits, which is far beyond reach. Only the fully degenerate case collapses.

But **algorithmic simplicity is the real hazard, and it is not the same thing as low
diversity**:

| Pattern over 99 rolls | Candidates an attacker precomputes | Effective bits |
|---|---|---|
| All one face | 6 | 2.6 |
| Two alternating faces (`121212…`) | 30 | 4.9 |
| Repeating 3-cycle (`123123…`) | 120 | 6.9 |
| Any repeating block of length ≤ 6 | 55,986 | 15.8 |

## The actionable insight

**A "distinct values" check would be the wrong check.** The obvious guard — count how
many faces appear and reject if too few — passes `123123123…` with three distinct faces
looking perfectly healthy, at 6.9 bits. It also *rejects* two-faces-only input that
actually carries 99 bits. It gets both directions wrong.

The family that matters is compressible sequences, so the right guard is a
compressibility or repetition test, not a diversity test. A cheap version: reject if the
zlib-compressed roll string is shorter than some fraction of its length, which catches
constant, alternating, cyclic and block-repeating input in one rule while passing genuine
low-diversity entries. This costs microseconds and needs no new UI beyond a warning.

## Severity: LOW — and deliberately so

This is user-caused and user-visible. A user must actively decide to type the same digit
99 times rather than roll a die, which means defeating the entire point of the ceremony
they chose to perform. That is categorically different from the Coldcard defect, where
the *device* silently produced low entropy while every indicator looked healthy.

Worth noting the parallel the postmortem itself draws: Coldcard's dice-only import path
was *exempt* from their defect, precisely because it never touched the device generator.
SeedSigner's dice path has the same structural property and the same immunity.

The coin-flip path (`generate_mnemonic_from_coin_flips`, 128 or 256 flips, same SHA-256
construction) has identical properties and the same gap; any guard should cover both.

**Recommendation:** add a compressibility warning, not a hard block — a user who
genuinely wants a weak seed for testing should still be able to make one, and a hard
block on a screen the user cannot get past would be worse than the problem. This is a
nice-to-have, not a defect.
