"""Evaluate the 'shake a handful of dice in a box, read left to right' recommendation.

The claim to test: does drawing each roll from a POOL of dice improve entropy
compared with rolling one die repeatedly?

Mechanism: after shaking, which physical die lands in which position is itself
random, so each reading is drawn from the AVERAGE of the pool's distributions.
Averaging independent biases pulls the mixture toward uniform.
"""
import math, random
random.seed(20260731)

def min_ent(p): return -math.log2(max(p))

def random_biased_die(severity, rng):
    """A die with an idiosyncratic bias of the given severity."""
    w = [max(0.01, 1 + rng.gauss(0, severity)) for _ in range(6)]
    t = sum(w)
    return [x / t for x in w]

rng = random.Random(20260731)
TRIALS = 4000
POOLS = tuple(range(1, 11))

print("=" * 78)
print("HOW MANY DICE IN THE BOX?  min-entropy per roll; a fair die = 2.585 bits")
print("Each trial draws 10 idiosyncratically biased dice; a pool of n uses the first n,")
print("so the columns are the same dice, not independent redraws. n=1 is one die rolled")
print("repeatedly.")
print("=" * 78)
print(f"{'worst face':<14}" + "".join(f"{n:>7}" for n in POOLS) + f"{'gain':>8}")
print("-" * 92)

# Severities are quoted by the unfairness they produce (mean excess of the worst face over
# 1/6), so the tiers can be compared with the measured dice: Labby 2009 gives 1.3%, and the
# published document works from a conservative 2%.
for severity, label in ((0.015,"2% unfair"),(0.05,"6% unfair"),
                        (0.10,"13% unfair"),(0.20,"26% unfair")):
    totals = {n: 0.0 for n in POOLS}
    for _ in range(TRIALS):
        dice = [random_biased_die(severity, rng) for _ in range(10)]
        for n in POOLS:
            mix = [sum(d[f] for d in dice[:n]) / n for f in range(6)]
            totals[n] += min_ent(mix)
    means = {n: totals[n] / TRIALS for n in POOLS}
    print(f"{label:<14}" + "".join(f"{means[n]:>7.3f}" for n in POOLS)
          + f"{means[10]-means[1]:>8.3f}")

print("\n" + "=" * 78)
print("THE CASE IT DOES NOT HELP: a whole batch sharing one systematic defect")
print("=" * 78)
for p6, lbl in ((0.20,"every die favours 6 at 20%"),(0.25,"every die favours 6 at 25%")):
    others = (1 - p6) / 5
    d = [others]*5 + [p6]
    mix = [sum(x[f] for x in [d]*10)/10 for f in range(6)]
    print(f"  {lbl:<34} single {min_ent(d):.3f}   pool of 10 {min_ent(mix):.3f}  (no gain)")

print("\n  Averaging cancels bias only when the biases DIFFER. Ten identical dice from")
print("  one bag, sharing a manufacturing defect, average to the same defect.")

print("\n" + "=" * 78)
print("TOTAL SEED STRENGTH, ordinary-quality dice")
print("=" * 78)
sev = 0.05
singles, pools = [], []
for _ in range(TRIALS):
    dice = [random_biased_die(sev, rng) for _ in range(10)]
    singles.append(min_ent(dice[0]))
    pools.append(min_ent([sum(d[f] for d in dice)/10 for f in range(6)]))
s, p = sum(singles)/TRIALS, sum(pools)/TRIALS
for n, need, lbl in ((50,128,"12-word"),(99,256,"24-word")):
    print(f"  {lbl}: one die {min(need,n*s):7.1f} bits   pool of 10 {min(need,n*p):7.1f} bits   (need {need})")
