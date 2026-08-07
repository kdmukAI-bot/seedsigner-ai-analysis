"""Verify an instrumented SeedSigner OS image really contains the instrumentation.

Usage:  python3 verify-image.py <image.img>

Checking the staged source tree is not sufficient. A build can succeed while the overlay
that was actually baked in is stale, and the resulting image looks correct from the outside.
This reads the app source back out of the finished artefact.

Why it is fiddly: the app lives in a gzipped cpio initramfs, embedded inside the gzipped
kernel, inside the zImage, inside a FAT partition. So the search is two decompression
levels deep. Note also that `gzip.decompress()` raises on trailing data and will silently
find nothing here -- a tolerant zlib decompressobj is required.

Exit status 0 if every check passes, 1 otherwise.
"""
import re
import struct
import sys
import zlib

# Present in a correctly instrumented image.
REQUIRED = [
    (b"BURST-DEBUG", "version stamp"),
    (b"BURST INSTRUMENTATION", "patch marker"),
    (b"microsd_free_bytes", "pre-flight free-space check"),
    (b"ABORTED: insufficient free space", "space abort path"),
    (b"ae_%s: exposure_speed", "AE state logger"),
    (b"before_lock", "AE pre-lock sample"),
    (b"after_burst", "AE post-burst sample"),
    (b"ae_window_s", "phase configuration"),
    (b"preview_frames_chained", "preview-chain count"),
    (b"preview_distinct_frames", "preview whole-window distinctness"),
    (b"preview_frames_dumped", "preview sample dump"),
    (b"preview_extra_dumped", "digest-coverage extra dump"),
    (b"BURST_PREVIEW_TIMING", "preview-loop timing collector"),
    (b"preview_loop_rate_fps", "loop-rate logging"),
    (b"delivery_rate_fps", "delivery-rate logging"),
    (b"preview_warmup_s", "camera warm-up timing"),
    (b"digest=%s", "preview per-frame digest logger"),
    (b"unit_id", "unit identity"),
    (b"quiet_period_s", "quiet period"),
    (b"capture_s=%.3f", "per-frame timing"),
    # No-seed kill-switch (added 2026-08-07, patched separately). Images built before it
    # legitimately fail these two checks; that is the intended verdict -- rebuild rather
    # than flash a capture image that can still turn its dumped bytes into a seed.
    (b"NO-SEED KILL-SWITCH", "seed-creation kill-switch marker"),
    (b"Seed creation disabled", "kill-switch user-facing notice"),
]

# Must NOT be present. Superseded code whose presence means a stale overlay was baked in.
FORBIDDEN = [
    (b"mean=%.4f", "superseded in-loop mean computation"),
    (b"sha256=%s", "superseded in-loop hashing"),
    # Stock image-to-mnemonic derivation, deleted by the kill-switch patch. Either needle
    # present means the build can still derive a seed from the bytes it wrote to the card.
    (b"seed_entropy_image", "stock image-to-seed derivation"),
    (b"mnemonic_generation.generate_mnemonic_from_bytes(", "stock mnemonic call site"),
]


def fat_offset(path):
    """First partition's byte offset, from the MBR."""
    with open(path, "rb") as f:
        mbr = f.read(512)
    if mbr[510:512] != b"\x55\xaa":
        raise SystemExit("not an MBR-partitioned image")
    for i in range(4):
        e = mbr[446 + i * 16: 446 + (i + 1) * 16]
        if any(e):
            lba, _ = struct.unpack("<II", e[8:16])
            return lba * 512
    raise SystemExit("no partitions found")


def inflate(buf, limit=400_000_000):
    """Decompress a gzip stream, tolerating trailing data (gzip.decompress cannot)."""
    d = zlib.decompressobj(16 + zlib.MAX_WBITS)
    out = bytearray()
    try:
        out += d.decompress(buf, limit)
    except Exception:
        pass
    return bytes(out)


def find_rootfs(image):
    """Return the decompressed cpio containing the app, or None."""
    data = open(image, "rb").read()
    for m in re.finditer(b"\x1f\x8b\x08", data):
        stage1 = inflate(data[m.start():])
        if len(stage1) < 1_000_000:
            continue
        for m2 in re.finditer(b"\x1f\x8b\x08", stage1):
            stage2 = inflate(stage1[m2.start():])
            if len(stage2) < 1_000_000:
                continue
            if b"BURST INSTRUMENTATION" in stage2 or b"seedsigner" in stage2:
                return stage2
    return None


def main(image):
    print(f"image: {image}")
    try:
        print(f"first partition at byte {fat_offset(image)}")
    except SystemExit as e:
        print(f"  warning: {e}")

    rootfs = find_rootfs(image)
    if rootfs is None:
        print("FAIL: could not locate the app rootfs inside the image")
        return 1
    print(f"rootfs cpio found, {len(rootfs):,} bytes\n")

    ok = True
    print("required:")
    for needle, desc in REQUIRED:
        n = rootfs.count(needle)
        ok &= n > 0
        print(f"  {'ok     ' if n else 'MISSING'}  {desc:<34} {n}")

    print("forbidden:")
    for needle, desc in FORBIDDEN:
        n = rootfs.count(needle)
        ok &= n == 0
        print(f"  {'ok     ' if not n else 'PRESENT'}  {desc:<34} {n}")

    # Capture phases actually configured. The REQUIRED list above only proves the phase
    # machinery is present ("ae_window_s"); it says nothing about how many phases will run.
    # That is the difference between a ~35 s capture and a ~60 s one, and between a dataset
    # that is uniformly release-behaviour and one carrying a non-release AE window. Read the
    # PHASES tuple out of the image and report it, so the configuration is asserted rather
    # than assumed. Comments are ignored: only entries inside the tuple count.
    m = re.search(rb"PHASES\s*=\s*\((.*?)\)\s*(?:#|\r?\n)", rootfs, re.S)
    if not m:
        ok = False
        print(f"  {'MISSING':<7}  {'PHASES tuple':<34} not found")
    else:
        phases = re.findall(rb'\("([^"]+)"\s*,', m.group(1))
        names = [p.decode() for p in phases]
        # Any phase other than the stock 0.25 s window is not v0.8.7 behaviour. Not an
        # error -- it is a legitimate probe -- but it must never pass silently.
        non_stock = [n for n in names if n != "stock"]
        print(f"  {'ok     ' if names else 'MISSING'}  {'capture phases configured':<34} "
              f"{len(names)}: {','.join(names) if names else 'none'}")
        ok &= bool(names)
        if non_stock:
            print(f"  {'NOTE   '}  {'non-release phase present':<34} {','.join(non_stock)}")
            print(f"           frames from it do NOT characterise v0.8.7; keep them out of "
                  f"release-baseline results")

    # Host bytecode contamination. The device compiles everything to one interpreter tag;
    # running python over the source tree on a build host with a different version leaves
    # __pycache__ behind, which cp -a then copies into the overlay. Two distinct tags in one
    # image means exactly that. Checking for a hardcoded tag would be wrong -- the device's
    # own version is legitimate and varies by OS release.
    tags = sorted({t.decode() for t in set(re.findall(rb"cpython-3\d\d", rootfs))})
    contaminated = len(tags) > 1
    ok &= not contaminated
    print(f"  {'ok     ' if not contaminated else 'PRESENT'}  "
          f"{'host bytecode contamination':<34} tags={','.join(tags) if tags else 'none'}")

    print()
    print("PASS - instrumentation verified inside the image" if ok
          else "FAIL - image does not match expectations, do not flash")
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    sys.exit(main(sys.argv[1]))
