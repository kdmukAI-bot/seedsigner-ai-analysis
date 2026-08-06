"""Review-screen display simulation for every retained final-image burst.

Usage:  python3 analyze_review_screen.py                  # all retained dataN bursts
        python3 analyze_review_screen.py <run_dir> [...]  # specific runs

v0.8.7's capture-review screen displays `ImageOps.autocontrast(final_image, cutoff=2)`.
On a fully dark frame that call returns the image byte-identical (red and blue fall below
the 2% cut; green collapses to a single level), so the screen shows pure black; anything
else stretches into a faintly visible image. This script replays that exact call over
every dumped final and reports, per frame, which display the user would have seen.

Version sensitivity: the classification depends on Pillow's autocontrast. SeedSigner OS
v0.8.7 ships Pillow 11.0.0 (buildroot `bf2a2858`, `package/python-pillow/python-pillow.mk`);
the published per-frame counts were computed at 11.0.0 and verified byte-identical under
11.1.0. Re-run under other versions before comparing against the published tables.

The load-bearing findings this reproduces (see evidence.html, IE-M-15): the display class
flickers between consecutive finals of one unchanged setup, frames displaying a faint
image occur in runs measuring as low as 113 bits, and frames displaying pure black occur
in runs measuring 1,958 -- so the review screen bounds entropy in neither direction.
"""
import sys
from pathlib import Path

import numpy as np
import PIL
from PIL import Image, ImageOps

HERE = Path(__file__).resolve().parent

SIZES = {480 * 480 * 3: 480, 640 * 640 * 3: 640}


def simulate(run: Path) -> None:
    frames = sorted((run / "stock").glob("frame*.raw"))
    if not frames:
        print(f"{run}: no stock frames")
        return
    pattern = []
    for f in frames:
        a = np.fromfile(f, np.uint8)
        n = SIZES.get(a.size)
        if n is None:
            print(f"{run}: unexpected frame size {a.size}")
            return
        a = a.reshape(n, n, 3)
        ac = ImageOps.autocontrast(Image.fromarray(a), cutoff=2)
        pattern.append("B" if (np.asarray(ac) == a).all() else "S")
    p = "".join(pattern)
    rel = run.relative_to(HERE) if run.is_relative_to(HERE) else run
    print(f"{str(rel):40s} {p}  ({p.count('S')} of {len(p)} display an image)")


print(f"Pillow {PIL.__version__}  (shipped version at OS tag v0.8.7: 11.0.0)")
print("B = byte-identical after autocontrast, displays pure black; S = stretched, displays a faint image")
runs = [Path(a) for a in sys.argv[1:]]
if not runs:
    for series in ("data1", "data2", "data3", "data4", "data5"):
        runs.extend(sorted((HERE / series).glob("burst-*")))
for r in runs:
    simulate(r)
