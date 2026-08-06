"""Evaluate the 'shake ten dice in a box, read left to right' recommendation.

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

print("=" * 78)
print("TEN DICE IN A BOX vs ONE DIE, ROLLED REPEATEDLY")
print("min-entropy per roll; a fair die = 2.585 bits")
print("=" * 78)
print(f"{'dice quality':<26}{'single die':>14}{'pool of 10':>14}{'bits regained':>16}")
print("-" * 78)

for severity, label in ((0.05,"very good"),(0.15,"ordinary"),(0.30,"poor"),(0.50,"bad")):
    singles, pools = [], []
    for _ in range(TRIALS):
        dice = [random_biased_die(severity, rng) for _ in range(10)]
        singles.append(min_ent(dice[0]))                     # roll die #1 repeatedly
        mix = [sum(d[f] for d in dice) / 10 for f in range(6)]
        pools.append(min_ent(mix))                            # read from the pool
    s, p = sum(singles)/TRIALS, sum(pools)/TRIALS
    print(f"{label:<26}{s:>14.3f}{p:>14.3f}{p-s:>16.3f}")

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
sev = 0.15
singles, pools = [], []
for _ in range(TRIALS):
    dice = [random_biased_die(sev, rng) for _ in range(10)]
    singles.append(min_ent(dice[0]))
    pools.append(min_ent([sum(d[f] for d in dice)/10 for f in range(6)]))
s, p = sum(singles)/TRIALS, sum(pools)/TRIALS
for n, need, lbl in ((50,128,"12-word"),(99,256,"24-word")):
    print(f"  {lbl}: one die {min(need,n*s):7.1f} bits   pool of 10 {min(need,n*p):7.1f} bits   (need {need})")
