"""Render the dark-capture plates from data3/burst-19700101-000150-6b66.

The run behind the analysis's headline dark figure: final image 113 bits (worst pair,
frames 00 and 06), preview window holding 45 copies of the attacker-computable black
constant plus four live frames (indices 18, 19, 39, 42).

Plates:
  - final worst pair, as shot and amplified, plus their difference (105 changed values
    of 691,200 -- invisible without dilation, so the diff plate is 5x5 max-dilated and
    the caption must say so)
  - one live preview frame amplified (the near-binary green plane, 99.4% of pixels)
  - the difference between the two adjacent live frames 18 and 19 (820 changed bytes,
    no dilation needed) -- per-read novelty made visible

Processing parameters are fixed here so every plate can be regenerated: GAIN=60 linear,
dilation 5x5 max-filter on the final diff only.

One plate is version-sensitive: dark_review_stretch_frame08.png is the review screen's own
output, ImageOps.autocontrast(cutoff=2) applied to stock frame08, and the identity-vs-stretch
threshold depends on the Pillow version. Generate it with Pillow 11.0.0, the version
SeedSigner OS v0.8.7 ships (buildroot bf2a2858); see analyze_review_screen.py.
"""
from pathlib import Path

import numpy as np
import PIL
from PIL import Image, ImageOps

HERE = Path(__file__).resolve().parent
RUN = HERE / "data3" / "burst-19700101-000150-6b66"
OUT = HERE / "figures"

GAIN = 60

# Final image: worst-of-all-pairs is (frame00, frame06), 113 bits.
FA, FB = RUN / "stock" / "frame00.raw", RUN / "stock" / "frame06.raw"
# Preview: adjacent live frames (window indices 18 and 19).
PA, PB = RUN / "preview" / "frame18.raw", RUN / "preview" / "frame19.raw"


def save(arr, name):
    Image.fromarray(arr.astype(np.uint8)).save(OUT / name, optimize=True)
    print("wrote", name)


def dilate(a, k):
    p = k // 2
    padded = np.pad(a, ((p, p), (p, p), (0, 0)))
    stack = [np.roll(np.roll(padded, i, 0), j, 1)
             for i in range(-p, p + 1) for j in range(-p, p + 1)]
    return np.max(np.stack(stack), 0)[p:-p, p:-p]


fa = np.fromfile(FA, dtype=np.uint8).reshape(480, 480, 3)
fb = np.fromfile(FB, dtype=np.uint8).reshape(480, 480, 3)
fd = np.abs(fa.astype(np.int16) - fb.astype(np.int16))
print(f"final pair: {int((fd > 0).sum()):,} values differ of {fa.size:,} "
      f"({100 * (fd > 0).mean():.4f}%), max delta {int(fd.max())}")

pa = np.fromfile(PA, dtype=np.uint8).reshape(240, 240, 4)[:, :, :3]
pb = np.fromfile(PB, dtype=np.uint8).reshape(240, 240, 4)[:, :, :3]
pd = np.abs(pa.astype(np.int16) - pb.astype(np.int16))
print(f"live frame: {int((pa > 0).sum()):,} nonzero bytes, "
      f"green share {100 * (pa[:, :, 1] > 0).mean():.1f}% of pixels")
print(f"live pair 18v19: {int((pd > 0).sum()):,} bytes differ ({100 * (pd > 0).mean():.2f}%)")

save(fa, "dark_final_a_as_shot.png")
save(fb, "dark_final_b_as_shot.png")
save(np.clip(fa.astype(np.int32) * GAIN, 0, 255), "dark_final_a_x60.png")
save(np.clip(fb.astype(np.int32) * GAIN, 0, 255), "dark_final_b_x60.png")
save(np.clip(dilate(fd.astype(np.int32) * GAIN, 5), 0, 255),
     "dark_final_diff_x60_dilated5.png")
save(np.clip(pa.astype(np.int32) * GAIN, 0, 255), "dark_preview_live18_x60.png")
save(np.clip(pd.astype(np.int32) * GAIN, 0, 255), "dark_preview_diff18v19_x60.png")

# The review screen's own output for a stretching capture of this run (see docstring).
f8 = np.fromfile(RUN / "stock" / "frame08.raw", dtype=np.uint8).reshape(480, 480, 3)
ac = np.asarray(ImageOps.autocontrast(Image.fromarray(f8), cutoff=2))
print(f"review render (Pillow {PIL.__version__}): frame08 "
      f"{'IDENTITY (would display pure black)' if (ac == f8).all() else 'stretched'}")
save(ac, "dark_review_stretch_frame08.png")
