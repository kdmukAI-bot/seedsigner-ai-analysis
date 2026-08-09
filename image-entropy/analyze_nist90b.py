"""Full NIST SP 800-90B non-IID assessment inputs for every shipped capture series.

Usage:  python3 analyze_nist90b.py                  # build datasets + formula MCV, all series
        python3 analyze_nist90b.py data5/burst-19700101-000306-6b66/stock
        python3 analyze_nist90b.py --ea /path/to/ea_non_iid [series...]   # also run the tool

Why this script exists
----------------------
analyze_mcv.py computes ONE of SP 800-90B's ten non-IID estimators (most-common-value,
6.3.1). A full assessment takes the MINIMUM over all ten, which can only sit at or below
MCV, and for a long time this document carried that gap as an unquantified caveat
(IE-L-01). This script builds the exact datasets the full assessment was run on, so the
sweep recorded in evidence/nist90b-sweep-results.tsv can be reproduced or challenged
with NIST's own reference tool.

The tool is not reimplemented here. Get it from
    https://github.com/usnistgov/SP800-90B_EntropyAssessment
build ea_non_iid (and ea_iid for the permutation tests), then either pass --ea or run it
by hand on the .bin files this script writes:
    ea_non_iid -i -a -v <series>_diff.bin 8

Dataset construction, and why it differs from analyze_mcv.py
------------------------------------------------------------
Value-by-value difference between captures, like every headline figure, but:

  * MOD-256, not signed. 90B symbols must fit one byte (Section 3.1.3 caps the alphabet
    at 256; the tool hard-limits bits_per_symbol to 1..8), and the signed domain spans
    -255..255. Mod-256 is the bijective choice; absolute value folds +k/-k together and
    moves the mode off zero on lit series. Dark series are domain-invariant (modal
    difference 0), so their figures compare directly to the published signed ones; lit
    figures do not, and a recomputation must match domains before filing a discrepancy.

  * POOLED over the five disjoint consecutive pairs (0-1, 2-3, 4-5, 6-7, 8-9), truncated
    to exactly 1,000,000 samples, because Section 3.1.1 requires at least 1,000,000
    sequential samples and one 480x480 pair is 691,200. Pooling sits between the average
    pair and the worst pair, so it is MILDLY OPTIMISTIC relative to the published
    worst-of-45 convention. The assessment's own minimum-over-estimators pushes the other
    way, and on every measured series the net figure landed well below the published MCV.

LIMITS -- read before quoting any number this produces. The ten estimators assume a
stationary source. A mixed-brightness scene (a dim bookshelf: near-black shelves,
isolated highlights) is a mixture of regimes, and the estimators punish it: the measured
whole-frame figure can land BELOW every brightness band of the same frames measured
separately. The result leans conservative, but it is an estimate, not a proven floor
(estimators can overestimate structured sources they cannot model), it is not tight, and
run-to-run spread on dim mixed scenes is large. Final images only: the preview layer has
not been assessed under the full suite, so chain-level restatements are inferences
except where a window contributed zero and the chain total IS the final-image figure.
"""
import glob
import math
import os
import subprocess
import sys

import numpy as np

N = 1_000_000


def mcv_bits_per_sample(x):
    """SP 800-90B 6.3.1 with the 99% upper confidence bound, per sample."""
    _, counts = np.unique(x, return_counts=True)
    p_hat = counts.max() / x.size
    p_u = min(1.0, p_hat + 2.576 * math.sqrt(p_hat * (1.0 - p_hat) / (x.size - 1)))
    return -math.log2(p_u)


def build(series_dir, out_dir):
    files = sorted(glob.glob(os.path.join(series_dir, "frame*.raw")))
    if len(files) < 2:
        return None
    sizes = [os.path.getsize(f) for f in files]
    modal = max(set(sizes), key=sizes.count)
    frames = [np.fromfile(f, dtype=np.uint8) for f, s in zip(files, sizes) if s == modal]
    if len({f.tobytes() for f in frames}) != len(frames):
        print(f"{series_dir}: *** DUPLICATE FRAMES -- series unsafe, not built")
        return None
    diffs = [((frames[i + 1].astype(np.int16) - frames[i].astype(np.int16)) % 256).astype(np.uint8)
             for i in range(0, len(frames) - 1, 2)]
    data = np.concatenate(diffs)[:N]
    if data.size < N:
        print(f"{series_dir}: only {data.size:,} samples available (< {N:,}); "
              f"the tool warns below 1M -- reported anyway")
    name = "_".join(series_dir.rstrip("/").split(os.sep)[-3:-1]).replace("burst-19700101-", "")
    path = os.path.join(out_dir, f"{name}_diff.bin")
    data.tofile(path)
    return path, modal, mcv_bits_per_sample(data)


if __name__ == "__main__":
    args = sys.argv[1:]
    ea = None
    if "--ea" in args:
        i = args.index("--ea")
        ea = args[i + 1]
        args = args[:i] + args[i + 2:]
    targets = args or sorted(glob.glob("data[1-9]/burst-*/stock"))
    out_dir = "nist90b-datasets"
    os.makedirs(out_dir, exist_ok=True)
    print(f"SP 800-90B INPUT DATASETS  (mod-256 diff, pooled disjoint pairs, {N:,} samples)")
    print("=" * 78)
    for t in targets:
        r = build(t, out_dir)
        if not r:
            continue
        path, frame_bytes, mcv = r
        print(f"{t:<44} {frame_bytes:>9,} B/frame   MCV {mcv:.4f} b/sample")
        if ea:
            print(subprocess.run([ea, "-i", "-a", path, "8"],
                                 capture_output=True, text=True).stdout)
    if not ea:
        print(f"\nDatasets in {out_dir}/. Run NIST's tool on each:")
        print("  ea_non_iid -i -a -v <file> 8")
        print("The assessment is min(H_original, 8 x H_bitstring) in its output.")
