"""Preview-window analysis for instrumented runs that dump the preview layer.

Usage:  python3 analyze_preview.py <run_dir> [<run_dir> ...]

Each run_dir is a burst-* directory containing capture.log, preview/frame*.raw
(RGBA, panel-sized) and stock/frame*.raw (RGB888 final-image burst). Runs from
instrumentation hash 78dc66ea onward log a SHA-256 digest for EVERY frame in the
rolling window; the dump is only a sample (all frames when the window held <= 20,
else the first 10 and last 10).

What this reports, and why it is not analyze_mcv.py
---------------------------------------------------
analyze_mcv.py refuses any series containing byte-identical frames, because for
the final-image burst a duplicate means the instrumentation failed. For the
preview window, duplicates are not a capture failure -- they are the finding.
A dim scene can quantize to a CONSTANT frame on the video-port path, so the
window's worst pair differences to zero and carries zero bits. This script
therefore reports the window's structure first and pair entropy second:

  * distinct count over the WHOLE window, from the logged digests (not just the
    dumped sample), plus integrity: dumped frames must re-hash to their logged
    digests
  * content class of each distinct frame: constant frames are reported with
    their value; non-constant frames with nonzero counts and value range
  * pairwise MCV (SP 800-90B 6.3.1, same formula as analyze_mcv.py) among the
    distinct dumped frames only, labelled by digest -- a pair of identical
    frames is 0 bits and is reported as such without ceremony
  * position overlap (Jaccard) of the changed-vs-constant masks between
    non-constant frames: near 1.0 means a fixed spatial pattern that an
    attacker can model, so between-live-frame MCV is the honest scale of the
    layer's per-frame contribution, not constant-vs-live MCV
  * with several runs: digests shared ACROSS runs. A byte-identical frame
    recurring in separate camera sessions is constant content, and an attacker
    does not need the device to know it

LIMITS: MCV assumes IID differences and these are not (spatial correlation,
fixed-pattern noise), so every figure printed here OVER-estimates the floor --
see entropy-estimator-pitfalls.md. Digest-count facts (distinct frames, shared
digests, mask overlap) are exact and carry no estimator caveat.
"""
import glob
import hashlib
import math
import os
import re
import sys

import numpy as np


def mcv_bits(a, b):
    """Same estimator, same confidence bound as analyze_mcv.py."""
    d = a.astype(np.int16) - b.astype(np.int16)
    _, counts = np.unique(d, return_counts=True)
    n = d.size
    p_hat = counts.max() / n
    p_u = min(1.0, p_hat + 2.576 * math.sqrt(p_hat * (1.0 - p_hat) / (n - 1)))
    return math.floor(n * -math.log2(p_u))


def parse_log(run_dir):
    """(window_digests, chained_count) from capture.log; digests keyed by index."""
    digests, chained = {}, None
    log_path = os.path.join(run_dir, "capture.log")
    if not os.path.exists(log_path):
        return digests, chained
    for line in open(log_path):
        m = re.match(r"preview (\d+): digest=([0-9a-f]{64})", line)
        if m:
            digests[int(m.group(1))] = m.group(2)
        m = re.match(r"preview_frames_chained: (\d+)", line)
        if m:
            chained = int(m.group(1))
    return digests, chained


def analyse(run_dir):
    digests, chained = parse_log(run_dir)
    files = sorted(glob.glob(os.path.join(run_dir, "preview", "frame*.raw")))
    if not digests and not files:
        print(f"{run_dir}: no preview data")
        return {}

    n_win = len(digests)
    distinct_win = len(set(digests.values()))
    print(f"{run_dir}")
    print(f"  window: {n_win} frames logged ({chained} chained), "
          f"{distinct_win} distinct, {len(files)} dumped")

    # Integrity: every dumped frame must re-hash to the digest logged for its
    # window index. A mismatch means the dump and the log describe different
    # captures and nothing below can be trusted.
    frames = {}
    for f in files:
        idx = int(re.search(r"frame(\d+)", os.path.basename(f)).group(1))
        raw = open(f, "rb").read()
        d = hashlib.sha256(raw).hexdigest()
        if idx in digests and digests[idx] != d:
            print(f"  *** INTEGRITY FAILURE: frame{idx:02d}.raw does not match "
                  f"its logged digest -- run unsafe, not reported")
            return {}
        frames[idx] = np.frombuffer(raw, dtype=np.uint8)
    print(f"  integrity: all dumped frames match their logged digests")

    # One representative per distinct digest among the dumped frames.
    by_digest = {}
    for idx, arr in sorted(frames.items()):
        d = digests.get(idx, hashlib.sha256(arr.tobytes()).hexdigest())
        by_digest.setdefault(d, (idx, arr))
    undumped = sorted(set(digests.values())
                      - {digests[i] for i in frames if i in digests})

    # Content class per distinct frame. RGBA: alpha is every 4th byte.
    reps = {}
    for d, (idx, arr) in by_digest.items():
        rgb = np.delete(arr.reshape(-1, 4), 3, axis=1)
        occurs = sum(1 for v in digests.values() if v == d)
        reps[d] = arr
        if rgb.max() == rgb.min():
            print(f"  {d[:8]} x{occurs:>2}  CONSTANT rgb={rgb.max()} "
                  f"(rep frame{idx:02d})")
        else:
            nz = int(np.count_nonzero(rgb))
            # Per-channel, because the structure of a near-threshold dark frame
            # is not spread evenly: green has twice the Bayer photosites and
            # unity AWB gain, so it crosses the rounding threshold first and a
            # "noisy" dark preview frame can be almost entirely one channel.
            ch = [int(np.count_nonzero(rgb[:, c])) for c in range(3)]
            print(f"  {d[:8]} x{occurs:>2}  live: nonzero={nz}/{rgb.size} "
                  f"({100*nz/rgb.size:.2f}%) max={rgb.max()} R/G/B={ch} "
                  f"(rep frame{idx:02d})")
    for d in undumped:
        occurs = sum(1 for v in digests.values() if v == d)
        print(f"  {d[:8]} x{occurs:>2}  NOT IN DUMP SAMPLE (content unknown; "
              f"distinctness known from the log)")

    # Pair entropy among distinct dumped frames. Identical pairs are 0 by
    # definition and every window with a repeated digest contains them, so the
    # window's worst pair is 0 bits whenever distinct < dumped.
    keys = list(by_digest)
    if distinct_win < n_win:
        print(f"  worst pair over window: 0 bits (repeated digests)")
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = reps[keys[i]], reps[keys[j]]
            ch = int(np.count_nonzero(a != b))
            print(f"  pair {keys[i][:8]}/{keys[j][:8]}: changed={ch} "
                  f"({100*ch/a.size:.2f}%) mcv={mcv_bits(a, b):,} bits")

    # Cached-buffer detection. Byte-identical CONSECUTIVE window slots holding
    # NON-constant content cannot be two independent sensor reads: distinct live
    # frames here differ in ~1-2% of bytes, so an exact repeat of ~230k bytes has
    # probability ~e^-3000. A repeat of a CONSTANT frame proves nothing (a dark
    # scene quantizes to the same constant every read), so only non-constant
    # repeats are reported. This is a fact about the code path and camera stack,
    # true in any room -- the most condition-independent thing here.
    consts = {d for d, (_, arr) in by_digest.items()
              if arr.reshape(-1, 4)[:, :3].max() == arr.reshape(-1, 4)[:, :3].min()}
    dup_runs = []
    for idx in sorted(digests):
        d = digests[idx]
        if dup_runs and dup_runs[-1][-1][1] == d and idx == dup_runs[-1][-1][0] + 1:
            dup_runs[-1].append((idx, d))
        else:
            dup_runs.append([(idx, d)])
    live_dups = [r for r in dup_runs if len(r) > 1 and r[0][1] not in consts
                 and r[0][1] in by_digest]
    if live_dups:
        for r in live_dups:
            print(f"  CACHED BUFFER: window slots {[i for i, _ in r]} are byte-identical "
                  f"non-constant frames ({r[0][1][:8]}) -- not separate sensor reads")
    elif any(len(r) > 1 for r in dup_runs):
        print(f"  (repeats present, all of constant frames -- consistent with "
              f"quantization, no caching demonstrated)")

    # Structure among live frames. Reported with a CHANCE BASELINE, because a
    # Jaccard over a dense mask is nearly free: for independent random sets of
    # density p and q, E[Jaccard] = pq/(p+q-pq), which is already 0.89 at p=q=0.94.
    # Quoting a raw 0.93 on such a mask as "fixed pattern" is an artifact. The
    # informative comparison is over the SPARSE side (the minority set), where
    # the chance baseline is low and excess overlap actually means something.
    live = [d for d in keys if d not in consts]
    if consts and len(live) >= 2:
        base = reps[sorted(consts)[0]]

        def jstats(ma, mb):
            i, u = int(np.sum(ma & mb)), int(np.sum(ma | mb))
            p, q = ma.mean(), mb.mean()
            exp = (p * q) / (p + q - p * q) if (p + q - p * q) else float("nan")
            return (i / u if u else float("nan")), exp

        for i in range(len(live)):
            for j in range(i + 1, len(live)):
                ma, mb = reps[live[i]] != base, reps[live[j]] != base
                dense = ma.mean() > 0.5
                jo, je = jstats(~ma, ~mb) if dense else jstats(ma, mb)
                which = "unchanged-set" if dense else "changed-set"
                ratio = jo / je if je else float("nan")
                print(f"  overlap {live[i][:8]}/{live[j][:8]} ({which}): "
                      f"jaccard={jo:.3f} vs chance={je:.3f} ({ratio:.1f}x) "
                      f"-- {100*(1-jo):.0f}% of the union churns")
        # Two complementary views, because either one alone misleads. A dark
        # live frame is near-binary: most subpixels cross the rounding threshold
        # together (predictable bulk), and the information is in the sparse
        # minority that does NOT cross. Report both, and let the volatile side
        # carry the entropy claim.
        chg = [reps[d] != base for d in live]
        core, union = np.logical_and.reduce(chg), np.logical_or.reduce(chg)
        print(f"  crossed in ALL {len(live)} live frames: {int(core.sum()):,} of "
              f"{int(union.sum()):,} ever-crossing positions "
              f"({100*core.sum()/max(union.sum(),1):.1f}%) -- the predictable bulk")
        # The minority: positions inside the active area that stayed put. These
        # are what distinguishes one live frame from another.
        held = [(~c) & union for c in chg]
        hcore, hunion = np.logical_and.reduce(held), np.logical_or.reduce(held)
        print(f"  held back in ALL {len(live)}: {int(hcore.sum()):,} of "
              f"{int(hunion.sum()):,} ever-held positions "
              f"({100*hcore.sum()/max(hunion.sum(),1):.1f}%) -- the rest varies "
              f"per read, and is where this layer's novelty lives")
    print()
    return {d: (arr, run_dir) for d, arr in
            ((k, v) for k, (_, v) in by_digest.items())}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    all_runs = {}
    for run_dir in sys.argv[1:]:
        all_runs[run_dir] = analyse(run_dir.rstrip("/"))

    if len(all_runs) > 1:
        print("ACROSS RUNS")
        digest_runs = {}
        for run_dir, reps in all_runs.items():
            for d in reps:
                digest_runs.setdefault(d, []).append(run_dir)
        shared = {d: rs for d, rs in digest_runs.items() if len(rs) > 1}
        if not shared:
            print("  no digest appears in more than one run")
        for d, rs in shared.items():
            print(f"  {d[:8]} appears in {len(rs)} runs: "
                  f"{', '.join(os.path.basename(r) for r in rs)}")
            print(f"           byte-identical content across separate camera "
                  f"sessions: constant, attacker-knowable without the device")
