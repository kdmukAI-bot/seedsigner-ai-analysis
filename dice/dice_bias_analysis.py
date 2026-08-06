"""What a biased die actually costs a SeedSigner seed.

Uses MIN-ENTROPY, -log2(max p_i), not Shannon entropy. Min-entropy is the conservative
measure for guessing attacks: it assumes the attacker knows the die's bias profile
perfectly and always guesses the most likely sequence first. Every number below is
therefore already a worst case.

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


SCENARIOS = [
    (1 / 6, "a perfectly fair die"),
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
    (128, "the standard 'secure against everything, forever' threshold"),
    (100, "still utterly out of reach of any conceivable attacker"),
    (80,  "uncomfortable for multi-decade storage; not currently breakable"),
    (64,  "breakable by a well-resourced attacker"),
    (40,  "breakable on a laptop"),
]:
    print(f"  {bits:>4} bits : {meaning}")

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
    for threshold in (128, 100, 80):
        needed_h = threshold / rolls
        p_needed = 2 ** (-needed_h)
        if p_needed <= FAIR:
            verdict = "impossible - a fair die already exceeds this"
        else:
            verdict = (f"one face would have to land {100*(p_needed/FAIR - 1):.0f}% "
                       f"more often than it should ({100*p_needed:.1f}% of rolls)")
        print(f"  {name} seed dropping to {threshold} bits: {verdict}")
    print()
