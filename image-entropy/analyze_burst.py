"""Consecutive-frame difference analysis for the v0.8.7 burst captures.

Usage:  python3 analyze_burst.py                                  # all retained dataN bursts
        python3 analyze_burst.py data2/burst-19700101-000409 [..] # specific runs

Input layout, as written by the instrumented v0.8.7 build:

    <run>/stock/frame00..09.raw     0.25 s auto-exposure window (stock v0.8.7 value)
    <run>/preview/frame*.raw        preview-window dumps (ignored by this script)
    <run>/capture.log               timing, AE state, unit id, configuration

(An optional long-ae phase exists commented-out in the patch; if re-enabled its
<run>/long-ae/ directory is analyzed the same way. No retained run carries one.)

Frames are 480x480 RGB888, 691,200 bytes -- the exact bytes v0.8.7 feeds into its
SHA-256 chain (`seed_entropy_image.tobytes()`), captured on the shipping picamera/MMAL
stack. A frame of any other length came from a different camera stack and is not
comparable with these figures.

Estimator matches the rest of the series: byte-wise difference between captures,
compressed with both bz2 and LZMA, smaller of the two, expressed in bits.
This is an UPPER bound -- a compressor is not an entropy oracle. For the floor-side
figure, which is what a security claim needs, use analyze_mcv.py.

Pass --all-pairs to compute every pairing rather than consecutive ones only. Consecutive
is not reliably the worst: a non-adjacent pair goes lower in four of six shipped series.

SIGN CONVENTION MATTERS HERE. The difference is taken as `later - earlier` and cast to
int8. Reversing the order shifts the compressed figure by up to ~1% (e.g. 13,488 becomes
13,584 on pi02w), because compressors are not symmetric in the sign of the residual.
Reproduce with this orientation or the published numbers will not match. The min-entropy
estimator has no such sensitivity.

Duplicate detection lives here rather than on the device: identical frames mean the
stack re-returned a cached frame, producing a difference of exactly zero that is
indistinguishable from collapsed entropy. Checking the delivered files also catches a
truncated or failed write, which a device-side check would miss.
"""
import bz2
import glob
import hashlib
import lzma
import os
import re
import sys

import numpy as np

W = H = 480
FRAME_BYTES = W * H * 3      # 691,200
NEEDED = 256                 # bits for a 24-word BIP-39 seed
ALL_PAIRS = "--all-pairs" in sys.argv


def compressed_bits(arr):
    raw = arr.tobytes()
    return 8 * min(len(bz2.compress(raw, 9)), len(lzma.compress(raw, preset=9)))


def load(phase_dir):
    """Frame geometry is not fixed: the final image is 2*max_dim square, so a 240x240
    panel gives 480x480 (691,200 B) and a 320x240 panel gives 640x640 (1,228,800 B).
    Take the modal size rather than assuming a panel, so Plus-display units are not
    silently discarded as malformed."""
    files = sorted(glob.glob(os.path.join(phase_dir, "frame*.raw")))
    if not files:
        return None, [], 0
    sizes = [os.path.getsize(f) for f in files]
    modal = max(set(sizes), key=sizes.count)
    files = [f for f, s in zip(files, sizes) if s == modal]
    return np.vstack([np.fromfile(f, dtype=np.uint8) for f in files]), files, modal


def analyse(run_dir):
    print("=" * 92)
    print(f"BURST CAPTURE  {run_dir}")
    print("=" * 92)

    log_path = os.path.join(run_dir, "capture.log")
    if os.path.exists(log_path):
        log = open(log_path).read()
        for field in ("board", "unit_id", "panel", "requested_resolution",
                      "quiet_period_s", "preview_frames_chained"):
            m = re.search(rf"^{field}: (.+)$", log, re.M)
            if m:
                print(f"  {field:<24} {m.group(1)}")
        gaps = [float(g) for g in re.findall(r"gap=([\d.]+)", log) if float(g) > 0]
        if gaps:
            print(f"  {'inter-frame gap s':<24} min {min(gaps):.3f}  mean {sum(gaps)/len(gaps):.3f}  max {max(gaps):.3f}")
        for m in re.finditer(r"--- phase: (\S+)\s+ae_window_s=([\d.]+).*?\n(.*?)(?=\n--- phase|\Z)",
                             log, re.S):
            ae = re.search(r"ae_after_burst: exposure_speed=(\d+) shutter_speed=\d+ "
                           r"analog_gain=([\d.]+) digital_gain=([\d.]+)", m.group(3))
            if ae:
                print(f"  AE locked [{m.group(1):<7} window={m.group(2):>5}s]  "
                      f"analog_gain={ae.group(2)}  digital_gain={ae.group(3)}  "
                      f"exposure={ae.group(1)}us")

    print()
    print(f"  {'phase':<9} {'frames':>6} {'mean':>7} {'bytes diff':>11} {'%':>7} "
          f"{'min':>11} {'median':>11} {'mean':>11} {'max':>11}")
    print("  " + "-" * 88)
    for phase in ("stock", "long-ae"):
        F, files, modal = load(os.path.join(run_dir, phase))
        if F is None:
            continue
        side = int(round((modal / 3) ** 0.5))
        Wp = Hp = side

        # Validity: every frame the expected size, and no repeats.
        bad = [f for f in files if os.path.getsize(f) != modal]
        digests = [hashlib.sha256(F[i].tobytes()).hexdigest() for i in range(F.shape[0])]
        if bad:
            print(f"  {phase:<9} *** {len(bad)} frame(s) not {modal} bytes -- unusable")
            continue
        if len(set(digests)) != len(digests):
            # A repeated frame differences to exactly zero, which is indistinguishable from
            # collapsed entropy. Refuse to report rather than publish a figure built on it.
            print(f"  {phase:<9} *** DUPLICATE FRAMES ({len(set(digests))} distinct of "
                  f"{len(digests)}) -- over-polled, series unsafe, not reported")
            continue

        # `later - earlier`, cast to int8. Both halves of that matter: see the module
        # docstring on sign sensitivity and serialization.
        if ALL_PAIRS:
            pairs = [(i, j) for j in range(F.shape[0]) for i in range(j)]
        else:
            pairs = [(i - 1, i) for i in range(1, F.shape[0])]
        est = np.array([compressed_bits((F[b].astype(np.int16) - F[a].astype(np.int16))
                                        .astype(np.int8))
                        for a, b in pairs])
        nd = np.mean([(F[i] != F[i - 1]).sum() for i in range(1, F.shape[0])])
        print(f"  {phase:<9} {F.shape[0]:>6} {F.mean():>7.2f} {int(nd):>11,} "
              f"{nd * 100.0 / F.shape[1]:>6.2f}% {est.min():>11,} {int(np.median(est)):>11,} "
              f"{int(est.mean()):>11,} {est.max():>11,}")
        print(f"  {'':<9} {'':>6} margin over {NEEDED}-bit seed, worst pair: "
              f"{est.min() // NEEDED:,}x")

        # Per-channel, and the share of positions that ever move -- the figures the
        # write-up quotes alongside the difference images.
        img = F.reshape(F.shape[0], Hp, Wp, 3)
        d01 = np.abs(img[1].astype(np.int16) - img[0].astype(np.int16))
        ch = [(d01[:, :, c] != 0).sum() for c in range(3)]
        changed = int((F != F[0]).any(axis=0).sum())
        print(f"  {'':<9} {'':>6} frame0->1 changed by channel: R {ch[0]:,}  G {ch[1]:,}  B {ch[2]:,}")
        print(f"  {'':<9} {'':>6} byte positions changing at least once: {changed:,} "
              f"({changed * 100.0 / F.shape[1]:.2f}%)")
    print()


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--all-pairs"]
    targets = args or sorted(glob.glob("data[1-9]/burst-*"))
    print(f"pairing: {'ALL pairs' if ALL_PAIRS else 'consecutive only'}"
          f"  (compressed estimator, UPPER bound)")
    for t in targets:
        analyse(t)
