"""Most-common-value min-entropy for every shipped capture series.

Usage:  python3 analyze_mcv.py                    # all shipped series
        python3 analyze_mcv.py data3/burst-19700101-000150-6b66/stock   # one series

Why this script exists
----------------------
`analyze_burst.py` computes the COMPRESSED estimate, which
bounds entropy from ABOVE. That is the wrong side for a security claim: an attacker
guessing seeds is limited by min-entropy, which bounds from BELOW. This script computes
the floor-side figure, so the numbers the analysis leads with are reproducible rather
than asserted.

Estimator
---------
The NIST SP 800-90B most-common-value method (SP 800-90B section 6.3.1), applied to the
value-by-value difference between two captures:

    d      = a - b                    (per byte position, signed)
    p_hat  = count(most frequent d) / len(d)
    p_u    = min(1, p_hat + 2.576 * sqrt(p_hat * (1 - p_hat) / (n - 1)))
    bits   = len(d) * -log2(p_u)      floored to an integer

The `p_u` step is the 99% upper confidence bound on the most-common value's probability,
and it is NOT optional. Omitting it -- taking -log2(p_hat) directly -- overstates the
floor, which is the anti-conservative direction for a security claim. It costs 1.7% to
6.9% on these datasets, and more on the sparser ones, which is exactly where the margin
is thinnest. An earlier version of this script omitted it.

The difference is taken as `later - earlier`. Unlike the compressed estimator, MCV is
invariant to that choice: mirroring the histogram preserves the largest count. It is also
invariant to signed/absolute/wraparound domain WHEN the modal difference is zero and
count(0) > count(+1) + count(-1), which holds for every blacked-out series here but NOT
for the lit ones, where taking absolute values moves the mode off zero and drops the
figure by about 30%. Signed is what this script reports.

Reported per series for two pair conventions, because they disagree:

  * worst of ALL pairs      -- every pairing; the conservative choice, and what the
                               analysis leads with
  * worst CONSECUTIVE pair  -- adjacent captures only, reported for continuity

LIMITS -- read before quoting any number this prints. Most-common-value assumes the
differences are IID. They are not: sensor noise is spatially correlated. A real
SP 800-90B assessment fails the IID test on this data and then takes the minimum across
ten non-IID estimators, every one of which can only return a figure AT OR BELOW this
one. So this is an over-estimate of the floor, not a measured floor. It is reported
because it bounds from the side that matters, not because it is tight.

The pair that minimizes the compressed estimate is NOT always the pair that minimizes
min-entropy. Selecting on one estimator and reporting the other overstates the floor;
this script selects on the estimator it reports.
"""
import glob
import math
import os
import re
import sys

import numpy as np

W = H = 480
FRAME_BYTES = W * H * 3      # 691,200
NEEDED = 256                 # bits for a 24-word BIP-39 seed


def mcv_bits(a, b):
    """Min-entropy of the a-b difference, SP 800-90B 6.3.1, floored.

    Returns (bits, p_u, p_hat) so a caller can see how much the confidence bound cost.
    """
    d = a.astype(np.int16) - b.astype(np.int16)
    _, counts = np.unique(d, return_counts=True)
    n = d.size
    p_hat = counts.max() / n
    p_u = min(1.0, p_hat + 2.576 * math.sqrt(p_hat * (1.0 - p_hat) / (n - 1)))
    return math.floor(n * -math.log2(p_u)), p_u, p_hat


def load(series_dir):
    """Both shipped layouts: <dir>/*-final.raw and <dir>/frame*.raw.

    Frame geometry is NOT fixed. The final image is 2*max_dim square, so a 240x240 panel
    gives 480x480 (691,200 bytes) and a 320x240 panel gives 640x640 (1,228,800 bytes).
    Hardcoding 480 silently discards every frame from a Plus-display unit. Take the modal
    size in the directory and drop anything disagreeing with it -- a short or truncated
    write is still caught, without assuming a panel.
    """
    files = sorted(glob.glob(os.path.join(series_dir, "*-final.raw")))
    if not files:
        files = sorted(glob.glob(os.path.join(series_dir, "frame*.raw")))
    if not files:
        return [], [], 0
    sizes = [os.path.getsize(f) for f in files]
    modal = max(set(sizes), key=sizes.count)
    odd = [f for f, s in zip(files, sizes) if s != modal]
    if odd:
        print(f"  ! dropping {len(odd)} frame(s) whose size != {modal:,}: "
              f"{', '.join(os.path.basename(f) for f in odd[:3])}")
    files = [f for f, s in zip(files, sizes) if s == modal]
    return [np.fromfile(f, dtype=np.uint8) for f in files], files, modal


def analyse(series_dir):
    frames, files, modal = load(series_dir)
    if len(frames) < 2:
        return
    # Two shipped pixel formats, not one: final/burst frames are RGB888 (3 B/px);
    # preview-window dumps are RGBA (4 B/px), because v0.8.7 converts preview frames
    # to RGBA before hashing and the dump is the exact hashed bytes. Try both. The two
    # square interpretations can never collide on one size (3s^2 = 4t^2 has no integer
    # solutions), so the order here is not load-bearing.
    side3 = int(round((modal / 3) ** 0.5))
    side4 = int(round((modal / 4) ** 0.5))
    if side3 * side3 * 3 == modal:
        geom, rgba = f"{side3}x{side3} RGB888", False
    elif side4 * side4 * 4 == modal:
        geom, rgba = f"{side4}x{side4} RGBA", True
    else:
        geom, rgba = f"{modal:,} B/frame", False
    # A repeated frame differences to exactly zero, which is indistinguishable from
    # collapsed entropy. Refuse to report rather than publish a figure built on it.
    if len({f.tobytes() for f in frames}) != len(frames):
        print(f"{series_dir:<28} *** DUPLICATE FRAMES -- series unsafe, not reported")
        return

    # Preview dumps keep the window index in the filename, and the sampling rule
    # (first 10 + last 10 of a >20-frame window) leaves a gap in the middle. Pairing
    # by list position across that gap would label a ~30-frames-apart pair
    # "consecutive". Pair by the indices the filenames carry; fall back to list
    # position only when the names carry no index (the *-final.raw layout).
    matches = [re.search(r"frame(\d+)", os.path.basename(f)) for f in files]
    idxs = [int(m.group(1)) for m in matches] if all(matches) else list(range(len(files)))
    consec = [(mcv_bits(frames[i], frames[i + 1])[0], i, i + 1)
              for i in range(len(frames) - 1) if idxs[i + 1] - idxs[i] == 1]
    skipped_gaps = (len(frames) - 1) - len(consec)
    allp = [(mcv_bits(frames[i], frames[j])[0], i, j)
            for i in range(len(frames)) for j in range(i + 1, len(frames))]
    wc, wa = min(consec) if consec else (None,), min(allp)

    print(f"{series_dir:<28} {len(frames):>3} frames, {len(allp):>3} pairs, {geom}")
    if rgba:
        # The chain hashes the alpha bytes, so the figures below include them. On
        # v0.8.7 the alpha plane is a constant added by the conversion and carries
        # nothing; in the dark regime its inclusion cancels out of MCV to first order
        # (it adds no changed values), and on lit frames it only lowers the figure.
        # Verify the constancy rather than assume it, and shout if it ever varies.
        alphas = {int(v) for f in frames for v in np.unique(f[3::4])}
        if len(alphas) == 1:
            print(f"  alpha: constant 0x{alphas.pop():02x} across series -- included "
                  f"in figures (neutral-to-conservative)")
        else:
            print(f"  ! alpha plane VARIES across series ({sorted(alphas)[:8]}) -- "
                  f"not the constant channel v0.8.7 adds; investigate before quoting")
    if skipped_gaps:
        print(f"  ! non-contiguous frame indices: consecutive stats use the "
              f"{len(consec)} truly-adjacent pairs; {skipped_gaps} gap pair(s) excluded")
    print(f"  worst of ALL pairs  {wa[0]:>12,} bits  {wa[0] // NEEDED:>7,}x   "
          f"pair({wa[1]},{wa[2]})   <- reported")
    if consec:
        print(f"  worst consecutive   {wc[0]:>12,} bits  {wc[0] // NEEDED:>7,}x   "
              f"pair({wc[1]},{wc[2]})")
        print(f"  consecutive range   {min(c[0] for c in consec):,} .. "
              f"{max(c[0] for c in consec):,}")
    _, p_u, p_hat = mcv_bits(frames[wa[1]], frames[wa[2]])
    without = math.floor(len(frames[0]) * -math.log2(p_hat))
    print(f"  p_hat {p_hat:.6f} -> p_u {p_u:.6f}   "
          f"confidence bound cost {without - wa[0]:,} bits ({100*(without-wa[0])/without:.1f}%)")
    print()


if __name__ == "__main__":
    targets = sys.argv[1:]
    if not targets:
        # All retained series: every run's final-image burst across the data rounds.
        targets = sorted(glob.glob("data[1-9]/burst-*/stock"))
    print(f"MOST-COMMON-VALUE MIN-ENTROPY  (a 24-word seed needs {NEEDED} bits)")
    print("=" * 78)
    for t in targets:
        if os.path.isdir(t):
            analyse(t)
