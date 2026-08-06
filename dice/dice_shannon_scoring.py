"""Would scoring the entered rolls with Shannon entropy catch a bad die?

Tests the proposal directly: compute the Shannon entropy of the empirical face
distribution of the rolls the user actually typed, and warn if it is too low.

Also tests the proposal's blind spot.
"""
import math
import random
import zlib
from collections import Counter

random.seed(20260731)  # deterministic, so this script reproduces exactly
TRIALS = 20000


def shannon(seq):
    """Shannon entropy of the empirical face distribution, in bits per roll."""
    n = len(seq)
    counts = Counter(seq)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def roll_biased(n, p_max, favoured="6"):
    """n rolls where `favoured` has probability p_max and the rest share the remainder."""
    others = [f for f in "123456" if f != favoured]
    p_other = (1 - p_max) / 5
    weights = [p_max] + [p_other] * 5
    return "".join(random.choices([favoured] + others, weights=weights, k=n))


def percentile(xs, q):
    xs = sorted(xs)
    return xs[int(q * (len(xs) - 1))]


print("=" * 84)
print("SHANNON SCORING OF THE ENTERED ROLLS")
print("A fair d6 has a maximum possible score of log2(6) = 2.585 bits/roll")
print("=" * 84)

for n_rolls in (50, 99):
    print(f"\n--- {n_rolls} rolls ---")
    print(f"{'die':<34}{'mean score':>12}{'5th pct':>10}{'1st pct':>10}")
    for p_max, label in [
        (1 / 6, "fair"),
        (0.20, "20% more often (visibly odd)"),
        (0.25, "50% more often (defective)"),
        (0.35, "110% more often (loaded)"),
        (0.50, "trick die"),
    ]:
        scores = [shannon(roll_biased(n_rolls, p_max)) for _ in range(TRIALS)]
        mean = sum(scores) / len(scores)
        print(f"{label:<34}{mean:>12.4f}{percentile(scores, 0.05):>10.4f}"
              f"{percentile(scores, 0.01):>10.4f}")

print("\n" + "=" * 84)
print("FINITE-SAMPLE BIAS - why the threshold cannot be 2.585")
print("=" * 84)
for n_rolls in (50, 99):
    scores = [shannon(roll_biased(n_rolls, 1 / 6)) for _ in range(TRIALS)]
    mean = sum(scores) / len(scores)
    print(f"  {n_rolls} rolls of a PERFECTLY FAIR die score {mean:.4f} on average, "
          f"not 2.585")
    print(f"    (expected downward bias ~(K-1)/(2N ln2) = "
          f"{5 / (2 * n_rolls * math.log(2)):.4f} bits)")
    print(f"    5th percentile {percentile(scores, 0.05):.4f}, "
          f"1st percentile {percentile(scores, 0.01):.4f}")

print("\n" + "=" * 84)
print("A WORKABLE THRESHOLD")
print("=" * 84)
for n_rolls in (50, 99):
    fair = [shannon(roll_biased(n_rolls, 1 / 6)) for _ in range(TRIALS)]
    thresh = percentile(fair, 0.001)  # falsely warn 1 honest user in 1000
    print(f"\n  {n_rolls} rolls, threshold {thresh:.3f} bits "
          f"(false-warning rate ~0.1% on a fair die):")
    for p_max, label in [(0.20, "20% more often"), (0.25, "50% more often"),
                         (0.35, "110% more often"), (0.50, "trick die")]:
        caught = sum(1 for _ in range(TRIALS)
                     if shannon(roll_biased(n_rolls, p_max)) < thresh)
        print(f"    catches a die landing one face {label:<18}: "
              f"{100 * caught / TRIALS:5.1f}% of the time")

print("\n" + "=" * 84)
print("THE BLIND SPOT - first-order entropy cannot see sequential structure")
print("=" * 84)
patterns = {
    "all sixes":                "6" * 99,
    "alternating 1,2":          "12" * 49 + "1",
    "repeating 1,2,3":          "123" * 33,
    "repeating 1,2,3,4,5,6":    "123456" * 16 + "123",
    "a real fair-die sequence": roll_biased(99, 1 / 6),
}
print(f"{'entered sequence':<28}{'Shannon':>10}{'verdict':>12}"
      f"{'zlib ratio':>13}{'verdict':>12}")
fair_ref = [shannon(roll_biased(99, 1 / 6)) for _ in range(TRIALS)]
s_thresh = percentile(fair_ref, 0.001)
zl_ref = [len(zlib.compress(roll_biased(99, 1 / 6).encode(), 9)) / 99
          for _ in range(2000)]
z_thresh = percentile(sorted(zl_ref), 0.001)

for name, seq in patterns.items():
    s = shannon(seq)
    z = len(zlib.compress(seq.encode(), 9)) / len(seq)
    print(f"{name:<28}{s:>10.3f}{'FLAG' if s < s_thresh else 'pass':>12}"
          f"{z:>13.3f}{'FLAG' if z < z_thresh else 'pass':>12}")

print(f"\n  Shannon threshold {s_thresh:.3f} bits/roll, "
      f"compression threshold {z_thresh:.3f} bytes/roll")
print("\n  Note the 1,2,3,4,5,6 row: a perfectly uniform face distribution, so it scores")
print("  the MAXIMUM on Shannon entropy while being entirely predictable. Compression")
print("  catches it because it sees the repetition. This is why the two checks belong")
print("  together - or why compression alone is the stronger single check.")
