"""Render the lit-scene plates from the shipping v0.8.7 burst captures.

Source: 480x480 RGB888, 691,200 bytes per frame, dumped from an instrumented v0.8.7 build
before hashing. Same pipeline, same geometry and same format as the blacked-out plates, so
the two sets are directly comparable.

Uses the `stock` phase of data1/burst-19700101-000303, the lit bookshelf baseline on the
Pi Zero Rev 1.3: `stock` is v0.8.7's real 0.25 s auto-exposure window, and this unit
carries the lowest lit baseline of the four, so the plates show the weaker case.

Plates are bare. Labels and captions live in index.html so they follow the page theme.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SRC = HERE / "data1" / "burst-19700101-000303" / "stock"
OUT = HERE / "figures"

W = H = 480
GAIN_LOW = 12                 # "every pixel that moved"
GAIN_HIGH = 40                # same difference, pushed harder
CROP = (150, 60, 246, 156)    # 96x96 detail region: book spines, mid-tone, sharp text
ZOOM = 6
BLINK_MS = 500


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

# One color per capture, so the strip flips hue as well as text. An identical strip on
# both frames made the swap easy to miss entirely: the wording changed, but nothing about
# the plate did, and the eye reads a caption as furniture rather than as signal.
#
# Blue and orange deliberately, for two reasons. It is the standard colorblind-safe
# opposed pair, so the alternation survives protanopia and deuteranopia, and it stays
# clear of every semantic color in series.css: green means verified, amber means caveat,
# and the crimson accent is structural. A capture index is none of those things, and a
# green-versus-red pair on two equally valid captures would read as pass-versus-fail.
LABEL_BG = {1: (27, 75, 122), 2: (193, 98, 30)}
LABEL_FG = (245, 241, 239)


def labeled(arr, index, text):
    """Frame plus a caption strip underneath, so the eye has an unambiguous swap cue.

    The strip is added BELOW the image rather than drawn over it: at this magnification
    every pixel is evidence, and covering any of it to label the figure would be the one
    edit this plate cannot afford. Color carries the cue and the text confirms it, so the
    swap is legible at a glance and still unambiguous on a static frame.
    """
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
    """Two-frame blink comparator, the astronomer's trick for spotting what moved.

    APNG rather than GIF, deliberately. GIF carries 256 colors and these crops hold far
    more, so a GIF would have to quantize; on this scene that hid more than half the change
    (97.8% of the crop's pixels differ, only 47.3% survived a shared 256-color palette).
    APNG is lossless, so every pixel that moved is a pixel the eye can see move, and the
    figure needs no caveat about the encoding. Browsers without APNG show frame one.

    Each frame carries its own caption strip in its own color. The sensor noise is subtle
    enough that without a hard swap cue a reader can stare at the animation and not
    register that anything is alternating at all; text alone was not enough, because a
    caption that only changes wording reads as furniture rather than as signal.
    """
    f0 = labeled(a, 1, "CAPTURE 1")
    f1 = labeled(b, 2, "CAPTURE 2")
    f0.save(OUT / name, save_all=True, append_images=[f1], duration=BLINK_MS, loop=0)
    src = int((a[::ZOOM, ::ZOOM] != b[::ZOOM, ::ZOOM]).any(axis=2).sum())
    n = a[::ZOOM, ::ZOOM].shape[0] * a[::ZOOM, ::ZOOM].shape[1]
    print(f"wrote {name}  ({BLINK_MS} ms/frame, lossless)")
    print(f"  crop pixels differing: {src:,}/{n:,} ({100*src/n:.1f}%)")


f0, f1 = load(SRC / "frame00.raw"), load(SRC / "frame01.raw")
diff = np.abs(f0.astype(np.int16) - f1.astype(np.int16))

nd = int((f0 != f1).sum())
print(f"frame00 mean {f0.mean():.2f}   frame01 mean {f1.mean():.2f}")
print(f"bytes differing: {nd:,} of {f0.size:,} ({100*nd/f0.size:.2f}%)")
print(f"delta: max {diff.max()}  mean over changed {diff[diff > 0].mean():.2f}")

save(f0, "09_lit_frame00_as_shot.png")
save(f1, "10_lit_frame01_as_shot.png")
save(np.clip(diff.astype(np.int32) * GAIN_LOW, 0, 255), "11_lit_difference_x12.png")
save(np.clip(diff.astype(np.int32) * GAIN_HIGH, 0, 255), "12_lit_difference_x40.png")
blink(zoom(f0), zoom(f1), "13_lit_detail_blink.png")
save(zoom(f0), "14_lit_detail_frame00.png")
save(zoom(f1), "15_lit_detail_frame01.png")
save(zoom(np.clip(diff.astype(np.int32) * GAIN_LOW, 0, 255)), "16_lit_detail_difference.png")

# Series-wide figures quoted in index.html.
F = np.stack([np.fromfile(p, np.uint8) for p in sorted(SRC.glob("*.raw"))])
changed = int((F != F[0]).any(axis=0).sum())
print(f"\nacross the 10-frame series: {changed:,} of {F.shape[1]:,} byte positions "
      f"changed at least once ({100*changed/F.shape[1]:.2f}%)")
print(f"gains x{GAIN_LOW} and x{GAIN_HIGH} clipped, native 480x480, detail {CROP} at "
      f"{ZOOM}x nearest-neighbour")
