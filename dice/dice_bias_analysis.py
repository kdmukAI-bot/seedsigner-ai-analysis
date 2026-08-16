"""What a biased die actually costs a seed.

Uses MIN-ENTROPY, -log2(max p_i), not Shannon entropy. Min-entropy is the conservative
way to count how many bits a distribution actually carries: it counts only the single
most likely face, so each row is a floor rather than an estimate.

Because only the maximum matters, the SHAPE of a bias does not change the answer:
a die with one face 2% high and a die with all three even faces 2% high carry
identical min-entropy. The last section shows this.

The MEASURED row is not a scenario. It is the per-face distribution reported by
Zacariah Labby, "Weldon's Dice, Automated", CHANCE 22(4), 2009, from 26,306 throws of
12 inexpensive white plastic dice with hollowed-out pips = 315,672 individual rolls:

    Pr1 = 0.1686  Pr2 = 0.1651  Pr3 = 0.1662
    Pr4 = 0.1658  Pr5 = 0.1655  Pr6 = 0.1688     (fair = 0.16667)

Every other row is hypothetical, and each is worse than anything that experiment found.

SHA-256 acts as a randomness extractor, so N rolls carrying H bits of min-entropy each
yield min(output_size, N*H) bits in the derived seed.
"""
import math

ROLLS_12, BITS_12 = 50, 128
ROLLS_24, BITS_24 = 99, 256
FAIR = 1 / 6


def min_entropy_per_roll(p_max):
    return -math.log2(p_max)


def rolls_to_detect(p_max, alpha_z=1.96, power_z=0.84):
    """Roughly how many test rolls to distinguish p_max from 1/6 (95% conf, 80% power)."""
    if abs(p_max - FAIR) < 1e-12:
        return float("inf")
    return ((alpha_z + power_z) ** 2) * p_max * (1 - p_max) / (p_max - FAIR) ** 2


LABBY_FACES = (0.1686, 0.1651, 0.1662, 0.1658, 0.1655, 0.1688)   # Labby 2009, 315,672 rolls

SCENARIOS = [
    (1 / 6, "a perfectly fair die"),
    (max(LABBY_FACES), "MEASURED: cheap dice, worst face"),
    (0.1683, "1% more often than it should"),
    (0.175, "5% more often"),
    (0.18, "8% more often"),
    (0.20, "20% more often - visibly odd"),
    (0.25, "50% more often - obviously defective"),
    (0.35, "110% more often - grossly loaded"),
    (0.50, "half of all rolls - a trick die"),
]

print("=" * 92)
print("WHAT A BIASED DIE COSTS YOU")
print("=" * 92)
print(f"{'favoured face lands':<34}{'bits/roll':>10}{'12-word':>12}{'24-word':>12}"
      f"{'test rolls to':>16}")
print(f"{'':<34}{'':>10}{'(50 rolls)':>12}{'(99 rolls)':>12}{'detect it':>16}")
print("-" * 92)

for p, label in SCENARIOS:
    h = min_entropy_per_roll(p)
    b12 = min(BITS_12, ROLLS_12 * h)
    b24 = min(BITS_24, ROLLS_24 * h)
    n = rolls_to_detect(p)
    n_s = "-" if n == float("inf") else f"{n:,.0f}"
    print(f"{label:<34}{h:>10.3f}{b12:>12.1f}{b24:>12.1f}{n_s:>16}")

print("-" * 92)
print(f"{'target':<34}{'':>10}{BITS_12:>12}{BITS_24:>12}")

print("\n" + "=" * 92)
print("SECURITY CONTEXT - what these numbers mean")
print("=" * 92)
for bits, meaning in [
    (256, "the theoretical maximum for a 24-word seed"),
    (128, "the security of the secp256k1 key itself; NIST's requirement from 2031"),
    (112, "NIST SP 800-57 Pt1 R5 Table 4: the minimum acceptable through 2030"),
    (80,  "uncomfortable for multi-decade storage; not currently breakable"),
    (64,  "breakable by a well-resourced attacker"),
    (40,  "breakable on a laptop"),
]:
    print(f"  {bits:>4} bits : {meaning}")

print("\n" + "=" * 92)
print("THE MEASURED DIE (Labby 2009)")
print("=" * 92)
p_m = max(LABBY_FACES)
h_m = min_entropy_per_roll(p_m)
print(f"  worst face lands {100*p_m:.2f}% of the time, {100*(p_m/FAIR - 1):.1f}% above its share")
print(f"    costs a 24-word seed  : {BITS_24 - min(BITS_24, ROLLS_24*h_m):.1f} bits "
      f"(leaving {min(BITS_24, ROLLS_24*h_m):.1f})")
print(f"    costs a 12-word seed  : {BITS_12 - min(BITS_12, ROLLS_12*h_m):.1f} bits "
      f"(leaving {min(BITS_12, ROLLS_12*h_m):.1f})")
print(f"    rolls needed to detect: {rolls_to_detect(p_m):,.0f}")
print(f"  Labby used {315672:,} rolls, which is why he could establish it (p = 0.00014).")

print("\n" + "=" * 92)
print("THE DETECTION PARADOX")
print("=" * 92)
p = 0.18
h = min_entropy_per_roll(p)
print(f"  A die favouring one face {100*(p/FAIR - 1):.0f}% more than it should:")
print(f"    costs a 24-word seed  : {BITS_24 - min(BITS_24, ROLLS_24*h):.0f} bits "
      f"(leaving {min(BITS_24, ROLLS_24*h):.0f})")
print(f"    costs a 12-word seed  : {BITS_12 - min(BITS_12, ROLLS_12*h):.0f} bits "
      f"(leaving {min(BITS_12, ROLLS_12*h):.0f})")
print(f"    rolls needed to detect: {rolls_to_detect(p):,.0f}")
print("\n  You would have to sit and roll the die thousands of times to notice a bias")
print("  that costs you a rounding error. Any bias large enough to actually matter is")
print("  large enough to spot in casual play.")

print("\n" + "=" * 92)
print("HOW BAD DOES IT HAVE TO GET?")
print("=" * 92)
for target, name in [(BITS_12, "12-word"), (BITS_24, "24-word")]:
    rolls = ROLLS_12 if target == BITS_12 else ROLLS_24
    for threshold in (128, 112, 80):
        needed_h = threshold / rolls
        p_needed = 2 ** (-needed_h)
        if p_needed <= FAIR:
            verdict = "impossible - a fair die already exceeds this"
        else:
            verdict = (f"one face would have to land {100*(p_needed/FAIR - 1):.0f}% "
                       f"more often than it should ({100*p_needed:.1f}% of rolls)")
        print(f"  {name} seed dropping to {threshold} bits: {verdict}")
    print()

print("=" * 92)
print("SHAPE OF THE BIAS, NOT JUST ITS SIZE")
print("=" * 92)
print("""  Iversen 1971 recorded only odd against even (P(even) = 0.5072), so the per-face
  split is an assumption, not a measurement. It turns out not to matter: min-entropy
  depends only on the single most likely face, so what counts is how high the worst
  face sits, not how many faces are elevated.""")

SHAPES = [
    ("fair", [FAIR] * 6),
    ("one face 2% high (the working figure)",
     [FAIR * 1.02] + [(1 - FAIR * 1.02) / 5] * 5),
    ("all three even faces 2% high",
     [FAIR * 1.02] * 3 + [(1 - 3 * FAIR * 1.02) / 3] * 3),
    ("Iversen, excess spread over 3 even faces", [0.5072 / 3] * 3 + [0.4928 / 3] * 3),
    ("Labby 1.3%, measured per-face", list(LABBY_FACES)),
]
print(f"\n  {'distribution':46}{'max face':>10}{'bits/roll':>11}{'24-word':>10}{'12-word':>10}")
for label, p in SHAPES:
    h = min_entropy_per_roll(max(p))
    print(f"  {label:46}{max(p):>10.5f}{h:>11.4f}"
          f"{min(BITS_24, ROLLS_24*h):>10.1f}{min(BITS_12, ROLLS_12*h):>10.1f}")
print("""
  The count of elevated faces does not enter the arithmetic: one face 2% high and all
  three even faces 2% high give the same seed strength, because min-entropy reads only
  the most likely face. Iversen's pattern at 1.44% a face costs less than either, so
  the 2% working figure bounds it whichever way the excess is distributed.""")
