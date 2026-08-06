"""Render the blank-wall plates from data5/burst-19700101-000306-6b66.

The stationary blank-wall run: the maximally boring capture. No scene detail, no camera
motion, no artificial light -- and a final image of 1,490,163 MCV bits (worst of all 45
pairs, frames 03 and 06). These plates are the visual answer to the "what if there is
nothing to look at?" worry.

Source: 480x480 RGB888, 691,200 bytes per frame, dumped from the same instrumented v0.8.7
build as every other retained series, before hashing. Same pipeline, geometry, format and
gains as the lit bookshelf plates (x12 / x40), so the two sets are directly comparable.

The wall is white; auto white balance renders it with a pale blue-green cast, and the soft
radial gradient is part window light, part natural lens vignetting. None of it matters to
the measurement.

Plates are bare. Labels and captions live in index.html so they follow the page theme.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SRC = HERE / "data5" / "burst-19700101-000306-6b66" / "stock"
OUT = HERE / "figures"

W = H = 480
GAIN_LOW = 12                 # same gains as the lit bookshelf set, for comparability
GAIN_HIGH = 40
CROP = (192, 192, 288, 288)   # 96x96 detail region: frame center, nothing in it but wall
ZOOM = 6
BLINK_MS = 500

# Worst-of-all-pairs by MCV is (frame03, frame06); analyze_mcv.py selects it.
FA, FB = SRC / "frame03.raw", SRC / "frame06.raw"


def load(p):
    return np.fromfile(p, dtype=np.uint8).reshape(H, W, 3)


def save(arr, name):
    Image.fromarray(arr.astype(np.uint8)).save(OUT / name, optimize=True)
    print("wrote", name)


def zoom(arr):
    img = Image.fromarray(arr.astype(np.uint8)).crop(CROP)
    return np.asarray(img.resize((img.width * ZOOM, img.height * ZOOM),
                                 Image.Resampling.NEAREST))


LABEL_H = 46          # strip below the image; nothing in the frame is covered
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

# Same blue/orange capture-index pair as the lit blink, for the same reasons: the standard
# colorblind-safe opposed pair, clear of the series' semantic colors (green = verified,
# amber = caveat), where a green-versus-red pair would read as pass-versus-fail.
LABEL_BG = {1: (27, 75, 122), 2: (193, 98, 30)}
LABEL_FG = (245, 241, 239)


def labeled(arr, index, text):
    """Frame plus a caption strip underneath, so the eye has an unambiguous swap cue."""
    h, w = arr.shape[:2]
    canvas = Image.new("RGB", (w, h + LABEL_H), LABEL_BG[index])
    canvas.paste(Image.fromarray(arr.astype(np.uint8)), (0, 0))
    d = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype(FONT, 24)
    except OSError:
        font = ImageFont.load_default()
    tw = d.textbbox((0, 0), text, font=font)[2]
    d.text(((w - tw) // 2, h + 11), text, fill=LABEL_FG, font=font)
    return canvas


def blink(a, b, name):
    """Two-frame blink comparator; APNG so no pixel is lost to palette quantization."""
    f0 = labeled(a, 1, "CAPTURE 1")
    f1 = labeled(b, 2, "CAPTURE 2")
    f0.save(OUT / name, save_all=True, append_images=[f1], duration=BLINK_MS, loop=0)
    src = int((a[::ZOOM, ::ZOOM] != b[::ZOOM, ::ZOOM]).any(axis=2).sum())
    n = a[::ZOOM, ::ZOOM].shape[0] * a[::ZOOM, ::ZOOM].shape[1]
    print(f"wrote {name}  ({BLINK_MS} ms/frame, lossless)")
    print(f"  crop pixels differing: {src:,}/{n:,} ({100*src/n:.1f}%)")


fa, fb = load(FA), load(FB)
diff = np.abs(fa.astype(np.int16) - fb.astype(np.int16))

nd = int((fa != fb).sum())
print(f"frame03 mean {fa.mean():.2f}   frame06 mean {fb.mean():.2f}")
print(f"bytes differing: {nd:,} of {fa.size:,} ({100*nd/fa.size:.2f}%)")
print(f"delta: max {diff.max()}  mean over changed {diff[diff > 0].mean():.2f}")

save(fa, "whitewall_final_a_as_shot.png")
save(fb, "whitewall_final_b_as_shot.png")
save(np.clip(diff.astype(np.int32) * GAIN_LOW, 0, 255), "whitewall_diff_x12.png")
save(np.clip(diff.astype(np.int32) * GAIN_HIGH, 0, 255), "whitewall_diff_x40.png")
blink(zoom(fa), zoom(fb), "whitewall_detail_blink.png")

# Series-wide figure quoted in captions.
F = np.stack([np.fromfile(p, np.uint8) for p in sorted(SRC.glob("*.raw"))])
changed = int((F != F[0]).any(axis=0).sum())
print(f"\nacross the 10-frame series: {changed:,} of {F.shape[1]:,} byte positions "
      f"changed at least once ({100*changed/F.shape[1]:.2f}%)")
print(f"gains x{GAIN_LOW} and x{GAIN_HIGH} clipped, native 480x480, detail {CROP} at "
      f"{ZOOM}x nearest-neighbour")
