# Capture rig — instrumented v0.8.7 test image

Everything needed to build a SeedSigner OS image that dumps the raw bytes v0.8.7 feeds into
its entropy hash, so the measurements in this analysis can be reproduced or challenged on
independent hardware.

```
build-instrumented-image.sh          one-shot build
verify-image.py                      confirms the instrumentation is inside the built image
0.8.7-burst-instrumentation.patch    the source change, applies to tag 0.8.7
0.8.7-no-seed-kill-switch.patch      deletes the image-to-mnemonic conversion, applies on top
```

**This build cannot turn a captured image into a seed.** The image bytes a seed would derive
from are written to the microSD in the clear, so rather than rely on a warning, the
image-to-mnemonic conversion is deleted outright by the kill-switch patch: after the
final-image review the flow shows "Seed creation disabled" and returns to the main menu. The
other seed paths (dice, manual entry) are stock and untouched by the instrumentation, but the
build stamps itself `0.8.7-BURST-DEBUG` on the splash and version screen and must never be
used as a wallet.

The kill-switch was added 2026-08-07, after the published capture rounds. It sits downstream
of every capture write, so it alters no measurement; the published data was captured on
builds without it, under the original "any seed generated on this build is compromised"
warning. It is a separate patch precisely so the burst patch's SHA-256, recorded in the
provenance of the captured data, stays intact. `verify-image.py` now requires the kill-switch
and fails pre-kill-switch images by design: rebuild rather than flash one.

---

## What it produces, and what it does not change

The instrumented build replaces v0.8.7's single final-image capture with **a burst of ten
frames** on the same scene, and instruments the live-preview layer: **every frame in the
rolling preview window is SHA-256 logged**, and a digest-coverage sample of them is dumped
(all frames when the window held 20 or fewer, otherwise the first and last 10 plus a
first-occurrence representative of every digest the positional sample missed). Each frame
plus a log is written to the microSD.

Left alone, deliberately:

- `hardware/camera.py` is **byte-identical to stock**. The capture path — `capture(stream,
  format='jpeg')`, the auto-exposure freeze, `Image.open(stream).rotate(...)` — is untouched.
- `resolution=(2*max_dim, 2*max_dim)` is unchanged, so frames are the same **480×480 RGB888,
  691,200 bytes** that v0.8.7 hashes via `seed_entropy_image.tobytes()`.
- The 0.25 s pre-capture window in phase 1 is stock v0.8.7.

Changed: the number of captures, the preview-window logging and dumping, and a one-line
`VERSION` string, across `views/tools_views.py`, `gui/screens/tools_screens.py` and
`controller.py`. The kill-switch patch then deletes the image-to-mnemonic conversion
(`ToolsImageEntropyMnemonicLengthView`'s derivation body), so the flow ends at a notice
instead of a seed.

Because it bursts rather than repeating whole capture flows, **it measures sensor noise
within one exposure state**, not the difference between two independent seed generations.
Frames in a burst share one AE lock and sit ~0.59 s apart.

### The capture phase

| Phase | AE window | What it is |
|---|---|---|
| `stock` | 0.25 s | exactly what v0.8.7 does |

`capture_frame()` freezes exposure on its **first** call (`exposure_mode='off'`), so the
0.25 s window before it decides the exposure state that every frame in the burst then
shares. (The patch also carries a commented-out `long-ae` 20 s phase, used in an earlier
round to probe a converged auto-exposure window; it is **not** v0.8.7 behavior and is not
captured by default.)

A 10 s quiet period runs first, with the **camera idle**, so the mechanical disturbance from
the button press settles. It sits before `start_single_frame_mode()` precisely so that it
does not extend the AE window and the burst keeps v0.8.7's real 0.25 s.

---

## Prerequisites

- **Docker**, usable without sudo.
- **seedsigner** app repo with tag `0.8.7` and the `seedsigner-translations` submodule
  checked out (`git submodule update --init --recursive`). At 0.8.7 the submodule is pinned
  to `708961a`.
- **seedsigner-os** repo at tag **`v0.8.7`**, with an `upstream` remote pointing at
  `github.com/SeedSigner/seedsigner-os`. The tag carries `BR2_PACKAGE_PYTHON_PICAMERA=y`
  and boots `start_x=1`, which is what v0.8.7's camera code needs: `picamera` is a ctypes
  wrapper over MMAL, so without that package the release's capture path has nothing to bind
  to and cannot run at all. The script checks the board defconfig and refuses to continue
  without it.
- **Both repos need the `upstream` remote configured**, because the provenance gate below
  verifies refs against it rather than against whatever the local clone calls `origin`.
  Override the remote name with `--upstream-remote` if yours differs.
- ~15 GB free disk (the build tree reaches ~10 GB with downloads). Network for the first
  build.

## Baseline provenance

**Every layer of the stack is pinned to an upstream release tag, and the build refuses to
proceed otherwise.** This is not ceremony. An earlier round of this measurement was
invalidated because the app layer was pinned to tag `0.8.7` while the OS layer was taken
from a convenience branch that existed only in a personal fork. The captured data looked
identical and recorded nothing about it, so the defect was invisible at analysis time.

Before building, `provenance_check()` resolves each ref to a commit and confirms it is
either reachable from an `upstream` branch or present as an `upstream` tag. If it cannot,
the build **stops**:

```
REFUSING TO BUILD. '<ref>' in <repo> cannot be traced to the upstream project via
remote 'upstream'. A measurement built on it does not characterise any released
device, and that will not be visible in the resulting data.
```

`--allow-unpinned-baseline` overrides the refusal, but it cannot hide it: the deviation is
written into `PROVENANCE.txt` as `*** NOT A RELEASE BASELINE ***`, and that file is meant to
travel with the captured frames. **A fork-based build can be made, but it cannot be mistaken
for a release-baseline one later.**

Every build writes `<work>/images/PROVENANCE.txt` recording both refs and their resolved
SHAs, whether each was upstream-verified, the upstream remote URL used, the SHA-256 of the
instrumentation patch, and the SHA-256 of the finished image. **Copy it alongside any data
you capture.** A capture set without it cannot be tied to a baseline afterwards.

## Build

```bash
./build-instrumented-image.sh --app /path/to/seedsigner --os /path/to/seedsigner-os --board pi0
```

`--board` takes `pi0` (default) or `pi02w`. The script clones seedsigner-os to a scratch
directory so the caller's working tree is never touched, then verifies the result.

Output: `<work>/images/seedsigner_os.0.8.7-BURST-DEBUG.<board>.img`

---

## Things that will bite you

Each of these silently breaks the build, or produces an image that looks fine and is not.
The build script handles all of them; they are documented because anyone modifying it will
hit them again.

**1. `version.json`, on OS revisions that demand it.** Some post-v0.8.7 OS revisions added a
`write_version_json()` step to `build.sh` that exits 1 without either `tools/write_versionfile.py`
or an existing `version.json`. That tool postdates app tag 0.8.7 — its `tools/` holds only
`mnemonic.py` and `seed_phrase_to_qr.py`, and the app reads its version from a hardcoded
`Controller.VERSION` — so the step cannot succeed and a stub must be pre-written. **Tag
`v0.8.7` does not have that step**, so on the default baseline this trap does not arise at
all; it was introduced by the fork branch an earlier round built from. The script greps
`build.sh` for `write_version_json` and writes the stub only when the OS revision actually
needs it.

**2. The translations submodule must be populated.** `git archive` does not include
submodules, and the build's catalog-compilation step fails partway through without it.

**3. The stock 50 MB image has ~5 MB free.** One run writes ~14 MB (20 × 691,200), so the
capture dies mid-burst with `No space left on device`. `post-image-seedsigner.sh` hardcodes
`dd ... count=50`; the script raises it to 256 MB, leaving ~220 MB.

**4. The download cache is not mounted.** The defconfigs set
`BR2_DL_DIR="$(TOPDIR)/../../buildroot_dl"`, which resolves to `/buildroot_dl` in the
container, and `docker-compose.yml` does not mount it. Without the added volume every build
redownloads ~1 GB.

**5. Host `__pycache__` leaks into the image.** Running python over the staged source tree
(a syntax check, say) leaves `__pycache__` behind, and `cp -a` copies it into the overlay and
then into the artefact. Mostly inert — the interpreter tag will not match the device's — but
it puts stale copies of edited code inside the image and makes verification ambiguous.
`verify-image.py` detects it by finding more than one distinct `cpython-3XX` tag.

**6. `.dev.` in the built filename does not mean a dev build.** The name is assembled from
`${seedsigner_app_repo_branch}`, still at its default because `--skip-repo` never clones. The
image is a normal single-partition release-layout build. Confirm with the partition table:
one FAT32 partition, not two.

**7. Verifying the staged source is not enough.** A build can succeed while baking in a stale
overlay. `verify-image.py` reads the app source back out of the finished image. That means
descending two gzip layers — the app is in a gzipped cpio initramfs inside the gzipped kernel
inside the zImage — and `gzip.decompress()` **raises on trailing data**, so it silently finds
nothing. A tolerant `zlib.decompressobj` is required.

---

## Running a capture

Flash the image, boot, and **confirm the splash reads `0.8.7-BURST-DEBUG`** before trusting
anything.

Then **New Seed → Image entropy**, once per scene. Aim on the live preview, click, then leave
the device alone: 10 s quiet, then the burst of ten. Under a minute. The final-image review
screen appears afterwards; accept or back out, the data is already written. Accepting shows
the "Seed creation disabled" notice and returns to the main menu: on this build the flow has
no seed to offer.

Rest the device on a table rather than holding it — a motionless device is the conservative
case, since any hand movement only adds to the measured difference. **Write down the scene
and lighting for each run**; nothing on the device records it.

### On the card

```
/mnt/microsd/burst-<stamp>-<unit>/stock/    frame00..09.raw   final images, 0.25 s AE window
                                 /preview/  frame*.raw        dumped preview-window frames (RGBA, panel-sized)
                                 capture.log                  incl. a SHA-256 digest for EVERY window slot
```

**Check the first stock `.raw` is 691,200 bytes** (480×480 RGB888 — 1,228,800 for a
640×640 Plus still), exactly what v0.8.7 hashes. Any other length means a different camera
stack is running and the set is unusable. Preview frames are panel-sized RGBA
(230,400 bytes at 240×240).

### The log records only what the frames cannot carry

Hashes, means, duplicate detection and every statistic are computed off-device from the
`.raw` files, so the capture loop does nothing but `capture_frame()` and a timestamp. An
earlier iteration computed them inline and stretched the inter-frame gap to 3.2 s; it is now
~0.59 s, which is the pipeline floor.

Per run: board, `unit_id` (sha256 of the CPU serial, truncated — identifies the unit without
publishing a hardware identifier), panel and requested resolution, quiet period, burst size,
`preview_frames_chained`, free space. Per phase: `ae_window_s`, camera revision, and AE state
both immediately before the lock and after the burst. Per frame: byte length, mode,
dimensions, inter-frame gap, capture latency.

---

## Analysis

```bash
python3 ../analyze_mcv.py <run>/stock          # final images: min-entropy, worst of all pairs
python3 ../analyze_preview.py <run>            # preview window: digest structure + pair MCV
python3 ../analyze_review_screen.py <run>      # what the review screen would have displayed
```

`analyze_mcv.py` asserts validity first — every frame the modal size, all distinct — and
refuses to report a final-image series with duplicates: a repeated frame differences to
exactly zero, which is indistinguishable from collapsed entropy. `analyze_preview.py` is the
opposite by design: in a preview window duplicates are the finding, so it reports them
(classified as constant or cached) rather than refusing. Import each session into its own
directory before analyzing: run names collide across devices and across boots of one device.

---

## Scope

This rig captures the **shipping v0.8.7 picamera/MMAL path**, which is the only camera stack
the reviewed release runs. Any future release that changes the camera pipeline needs its own
capture set: figures are not interchangeable across stacks, and nothing here transfers.

The capture is also downstream of the full ISP: black-level correction, demosaic, white
balance, **denoise**, tone curve, then JPEG encode and immediate decode. picamera exposes
`image_denoise` (default on, never set by v0.8.7) and a `bayer=True` capture option for
pre-ISP sensor data at full resolution. Neither is exercised here — this rig captures what
v0.8.7 actually hashes, not what the sensor could provide.
