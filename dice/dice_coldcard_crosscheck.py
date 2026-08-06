"""Cross-check SeedSigner's dice construction against Coldcard's shipping implementation.

Coldcard's algorithm, transcribed from Coldcard/firmware `shared/seed.py` at master:

    new_from_dice():        seed = b''
    add_dice_rolls():       md = sha256(seed)
                            for each keypress in '123456':  md.update(ch)
                            seed = md.digest()
    approve_word_list():    if nwords == 12: seed = seed[0:16]
                            words = bip39.b2a_words(seed)

Also evaluates Coldcard's low-quality-roll guard, which SeedSigner does not have:

    bad_dist = any((v / count) > 0.30 for _, v in counter.items())
"""
import hashlib
import math
import random
from collections import Counter

from mnemonic import Mnemonic

random.seed(20260731)
trezor = Mnemonic("english")

VEC_99 = ("655152231316521321611331544441236164664431121534415633526456254462245546236542364246312613322234612",
          "eyebrow obvious such suggest poet seven breeze blame virtual frown dynamic donor "
          "harsh pigeon express broccoli easy apology scatter force recipe shadow claim radio")
VEC_50 = ("65515223131652132161133154444123616466443112153441",
          "hole luggage safe present express tragic orbit shed switch metal identify path")


def coldcard_dice_to_words(rolls: str, nwords: int) -> str:
    """Coldcard's construction, transcribed from their source."""
    md = hashlib.sha256(b"")            # new_from_dice: seed = b''
    for ch in rolls:                    # add_dice_rolls: md.update(ch) per keypress
        md.update(ch.encode())
    seed = md.digest()
    if nwords == 12:                    # approve_word_list
        seed = seed[0:16]
    return trezor.to_mnemonic(seed)


def seedsigner_dice_to_words(rolls: str, nwords: int) -> str:
    """SeedSigner's construction, from helpers/mnemonic_generation.py."""
    entropy = hashlib.sha256(rolls.encode()).digest()
    if nwords == 12:
        entropy = entropy[:16]
    return trezor.to_mnemonic(entropy)


print("=" * 80)
print("SEEDSIGNER vs COLDCARD - same rolls, same words?")
print("=" * 80)
for label, (rolls, published) in (("99 rolls / 24 words", VEC_99), ("50 rolls / 12 words", VEC_50)):
    n = len(published.split())
    ss = seedsigner_dice_to_words(rolls, n)
    cc = coldcard_dice_to_words(rolls, n)
    print(f"\n  {label}")
    print(f"    SeedSigner == Coldcard        : {ss == cc}")
    print(f"    both == SeedSigner's published: {ss == published == cc}")

# Random rolls too, not just the published vectors.
mismatches = 0
for _ in range(2000):
    for n, cnt in ((24, 99), (12, 50)):
        r = "".join(random.choices("123456", k=cnt))
        if seedsigner_dice_to_words(r, n) != coldcard_dice_to_words(r, n):
            mismatches += 1
print(f"\n  4,000 random roll sequences, both lengths: {mismatches} mismatches")

# ---------------------------------------------------------------- the guard
print("\n" + "=" * 80)
print("COLDCARD'S LOW-QUALITY GUARD - which SeedSigner does not have")
print("  rejects if any single face exceeds 30% of the rolls")
print("=" * 80)


def coldcard_bad_dist(rolls: str) -> bool:
    c = Counter(rolls)
    n = len(rolls)
    return any((v / n) > 0.30 for v in c.values())


def shannon(s):
    n = len(s)
    return -sum((v / n) * math.log2(v / n) for v in Counter(s).values())


print("\n  False-warning rate on a genuinely fair die:")
for cnt in (50, 99):
    fp = sum(1 for _ in range(50000)
             if coldcard_bad_dist("".join(random.choices("123456", k=cnt))))
    print(f"    {cnt} rolls: {100 * fp / 50000:.3f}%")

print("\n  What it catches (99 rolls):")
pats = {
    "all sixes":              "6" * 99,
    "alternating 1,2":        ("12" * 99)[:99],
    "repeating 1,2,3":        ("123" * 99)[:99],
    "repeating 1,2,3,4,5,6":  ("123456" * 99)[:99],
    "a real fair sequence":   "".join(random.choices("123456", k=99)),
}
print(f"    {'sequence':<26}{'top face':>10}{'Coldcard 30%':>15}{'Shannon':>10}")
for name, seq in pats.items():
    top = max(Counter(seq).values()) / len(seq)
    print(f"    {name:<26}{100*top:>9.1f}%{'REJECT' if coldcard_bad_dist(seq) else 'accept':>15}"
          f"{shannon(seq):>10.3f}")

print("\n  Note the 1,2,3,4,5,6 row: every face lands exactly its fair share, so the")
print("  30% guard accepts a completely predictable sequence. Same blind spot as a")
print("  Shannon score - both measure WHICH faces appeared, not in what order.")

print("\n  Against a biased die (does the guard catch bias?):")
for p_max, lbl in ((0.20, "20% more often"), (0.25, "50% more often"),
                   (0.35, "110% more often"), (0.50, "trick die")):
    others = (1 - p_max) / 5
    caught = sum(1 for _ in range(20000)
                 if coldcard_bad_dist("".join(random.choices(
                     "123456", weights=[p_max] + [others] * 5, k=99))))
    print(f"    {lbl:<20}: caught {100*caught/20000:5.1f}% of the time")
