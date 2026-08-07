# Image/Camera Entropy Seed Generation — Complete Release History

**Scope:** Every SeedSigner release from the feature's introduction through v0.8.7.
**Method:** Read directly from git tags in `/home/kdmukai/dev/seedsigner` (`git show <tag>:<path>`, `git log`, `git diff <tag> <tag>`), plus upstream PR/issue bodies via `gh` against `SeedSigner/seedsigner`. Every claim is labeled **VERIFIED** (read from source at a specific tag/commit) or **INFERRED**.
**Date of research:** 2026-08-03.

---

## 1. Introduction of the feature

**VERIFIED:** Camera/image entropy seed generation first shipped in **v0.4.3 (tagged 2021-07-31)**. Tags 0.2.0 through 0.4.2 contain no camera-image seed code (grep across each tag for `from_camera_image` / image+entropy patterns: zero matches; the only "entropy" in earlier tags is dice-roll entropy).

- Development commit: `d7bea686` "End-to-end image-capture-as-seed functioning" (2021-07-12, author kdmukai), first contained in tag 0.4.3.
- Landed upstream inside **PR #46 "Passphrase keyboard"** (kdmukai, merged 2021-07-24), whose body explicitly lists: *"Adds image-based entropy for generating new seeds."* (VERIFIED via `gh pr view 46`.)
- Follow-up in the same release: `464afcf5` "Image seed fixes; reduced auto-exposure time" (2021-07-23).

### The v0.4.3 entropy chain (VERIFIED, quoted from `0.4.3:src/seedsigner/views/seed_tools_view.py`)

```python
hash = hashlib.sha256(self.seed_entropy_image.tobytes())
badseedphrase_str = mnemonic_from_bytes(hash.digest())
badseedphrase_list = badseedphrase_str.split()
badseedphrase_list.pop(-1)
calclastwordphrasestr = " ".join(badseedphrase_list) + " abandon"
goodphrasebytes = mnemonic_to_bytes(calclastwordphrasestr, ignore_checksum=True)
goodseedphrasestr = mnemonic_from_bytes(goodphrasebytes)
self.words = goodseedphrasestr.split()
```

And the capture (VERIFIED, `0.4.3:src/seedsigner/helpers/camera_process.py`):

```python
camera = picamera.PiCamera(resolution=(720, 480), framerate=8)
...
stream = io.BytesIO()
camera.capture(stream, format='jpeg')
stream.seek(0)
out_queue.put([Image.open(stream)])
```

**v0.4.3 characteristics:**
- **What is hashed:** exactly one thing — `SHA-256(final_image.tobytes())`. The image is a single 720×480 capture, **JPEG-encoded by the camera then decoded by PIL** to RGB (3 bytes/px, 1,036,800 bytes hashed).
- **No preview frames, no CPU serial, no `time.time()`** anywhere in the chain. There is no live preview at all in this version (the user sees a text modal "Aim camera / click joystick").
- **Words:** 24-word only. The "abandon trick" above discards the last word of the raw 24-word phrase (which carries the digest's final 3 entropy bits + 8 checksum bits), pins those 3 entropy bits to zero, and recomputes the checksum. **Effective use of the digest: 253 of 256 bits** (VERIFIED from the code above; the security impact of losing 3 bits is nil).

---

## 2. Per-release timeline of the entropy chain

Dates are the tag's commit dates (`git log -1 --format=%ad <tag>`), all VERIFIED.

| Tag | Date | Chain composition (in order) | Preview frames | Final image | Lossy stage | Digest bits used |
|---|---|---|---|---|---|---|
| **0.4.3** | 2021-07-31 | SHA-256(final image) only | **none — no preview layer exists** | 720×480 RGB (JPEG-decoded) | JPEG (camera-side encode) | 253 (24w only; "abandon trick") |
| **0.4.4** | 2021-08-27 | SHA-256(serial) → SHA-256(prev ‖ `str(time.time())`) → per-frame SHA-256(prev ‖ frame) → SHA-256(prev ‖ final image) | **first 50** frames, 240×240 raw RGB, appended **before** button check | 720×480 RGB (JPEG-decoded) | JPEG (final image only; previews are raw RGB) | 256 (24w only) |
| 0.4.5 | 2021-11-19 | unchanged | unchanged (adds screensaver input-time bookkeeping only) | unchanged (rotation moved into camera.py) | unchanged | unchanged |
| 0.4.6 | 2022-02-20 | unchanged (function body byte-identical to 0.4.5) | unchanged | unchanged | unchanged | unchanged |
| **0.5.0** | 2022-04-22 | same chain, ported to MVC (`tools_views.py` / `tools_screens.py`) | first 50, 240×240 RGB, append-before-check | 720×480, JPEG-decoded | JPEG | **256 (24w) or first 128 (12w)** — 12-word option introduced |
| 0.5.1 | 2022-06-17 | unchanged (entropy sections byte-identical to 0.5.0) | unchanged | unchanged | unchanged | unchanged |
| 0.5.1_EXP | — | unchanged (entropy sections byte-identical to 0.5.1) | unchanged | unchanged | unchanged | unchanged |
| 0.6.0 | 2023-02-16 | unchanged (byte-identical to 0.5.1) | unchanged | unchanged | unchanged | unchanged |
| **0.7.0** | 2023-09-04 | same chain | **last 50** (moving window); **loop restructured: click-check now returns *before* appending the current frame** | 720×480, JPEG-decoded | JPEG | unchanged |
| **0.8.0** | 2024-08-17 | same chain; serial-failure fallback now logs via `logger` | last 50; preview frames now **RGBA** (constant alpha byte added by `read_video_stream`'s `.convert('RGBA')`, commit `c1be23ff`) | 720×480, JPEG-decoded | JPEG | unchanged |
| **0.8.5** | 2025-02-01 | same chain | last 50; trigger widened from KEY_PRESS to **KEYS__ANYCLICK** (`[KEY_PRESS, KEY1, KEY2, KEY3]`) | 720×480, JPEG-decoded | JPEG | unchanged |
| **0.8.6** | 2025-06-21 | same chain | last 50; stream res now `max(canvas dims)²` (240×240 stock) | **480×480** on stock 240×240 displays (`2*max_dim` square), JPEG-decoded | JPEG | unchanged |
| 0.8.7 | 2026-06-09 | same chain, wrapped in `LoadingScreenThread` try/finally; camera errors raise `CameraConnectionError` | unchanged from 0.8.6 | unchanged from 0.8.6 | JPEG | unchanged |

Pre-release tags: 0.5.0-pre1 (2022-03-02) still carried the 0.4.6-era code; the MVC port with the 12-word option arrived in 0.5.0-pre2 (2022-03-15, commit `3554b470` "Initial image entropy seed creation port"). 0.7.0-rc1 is identical to 0.7.0 in these files; 0.8.5-rc1 differs from 0.8.5 only in screen cosmetics. (VERIFIED via per-tag diffs.)

### The canonical chain (VERIFIED, quoted from `0.5.0:src/seedsigner/views/tools_views.py`; byte-identical logic in every release 0.4.4 → 0.8.7)

```python
# Build in some hardware-level uniqueness via CPU unique Serial num
try:
    stream = os.popen("cat /proc/cpuinfo | grep Serial")
    output = stream.read()
    serial_num = output.split(":")[-1].strip().encode('utf-8')
    serial_hash = hashlib.sha256(serial_num)
    hash_bytes = serial_hash.digest()
except Exception as e:
    print(repr(e))
    hash_bytes = b'0'

# Build in modest entropy via millis since power on
millis_hash = hashlib.sha256(hash_bytes + str(time.time()).encode('utf-8'))
hash_bytes = millis_hash.digest()

# Build in better entropy by chaining the preview frames
for frame in preview_images:
    img_hash = hashlib.sha256(hash_bytes + frame.tobytes())
    hash_bytes = img_hash.digest()

# Finally build in our headline entropy via the new full-res image
final_hash = hashlib.sha256(hash_bytes + seed_entropy_image.tobytes()).digest()

if mnemonic_length == 12:
    # 12-word mnemonic only uses the first 128 bits / 16 bytes of entropy
    final_hash = final_hash[:16]
```

(0.8.0 changed `print(repr(e))` to `logger.info(...)`; 0.8.7 wrapped the block in a spinner try/finally. Nothing else in this block has changed since 0.4.4. VERIFIED by successive tag diffs of the extracted sections — 0.5.0→0.5.1→0.6.0 produced empty diffs.)

---

## 3. Every material change, with commit/PR and rationale

1. **0.4.3 — feature introduced** (`d7bea686`, PR #46, kdmukai). Single JPEG frame hashed; 24-word only. Rationale: first cut of "image-capture-as-seed."

2. **0.4.4 — chain hardened** (`bb54af05` "chaining camera entropy; mnemonic methods factored out; initial tests", 2021-08-20; **PR #76 "Moar camera entropy"**, merged 2021-08-22). PR body (VERIFIED): *"Enhances image-based entropy by chaining hashes from: the CPU's unique Serial, the millis since power on, each live preview image (up to 50 images), and then the final 720x480 entropy image."* Also removed the abandon trick (full 256-bit digest now used). This is the chain still shipping in 0.8.7.

3. **0.5.0 — MVC port + 12-word option** (`3554b470`, 2022-03-08). Chain logic copied verbatim; new mnemonic-length screen truncates the digest to 16 bytes for 12-word seeds (BIP-39-standard 128 bits).

4. **0.7.0 — preview-loop restructure** (`91b02061` "bugfix for entering image entropy via long click", 2023-08-23; **PR #453**, merged 2023-08-24; fixes **issue #450**). See §5 — this introduced the early-return-before-append shape *and* changed the 50-frame window from first-50 to last-50. PR body (VERIFIED): the pre-fix code could crash (`ValueError ... use 4-item box` in `PIL Image.paste`) when a long click raced the camera warm-up and `frame` was still `None`; the fix reordered the loop and *"Minor edit to preserve newer preview frames after max_entropy_frames has been reached; now cycles older frames out."*

5. **0.8.0 — preview frames become RGBA** (`c1be23ff` "implements progress bar"). `read_video_stream(as_image=True)` gained `.convert('RGBA')`, so each hashed preview frame is 240×240×4 with a constant alpha byte. Incidental to GUI work; adds constant bytes to the hash input, no entropy effect. (VERIFIED via `git log -S"convert('RGBA')"`.)

6. **0.8.5 — ANYCLICK trigger** (`03b6044f` "Allow ANYCLICK in image entropy flow", 2025-01-28, landed via PR #675 "v0.8.5_final_changes"). Final capture now triggers on any of `[KEY_PRESS, KEY1, KEY2, KEY3]` instead of KEY_PRESS alone (VERIFIED: `0.8.7:src/seedsigner/hardware/buttons.py` line 205). Usability change; slightly widens the held-button surface described in §5.

7. **0.8.6 — final image resolution change** (`639afc2e` "Aspect ratio-savvy camera frame resizing for non-square displays", 2025-04-19, **PR #741 "[New Feature] Support for 320x240 displays"**). Final capture went from fixed `(720, 480)` to `(2*max_dim, 2*max_dim)` where `max_dim = max(canvas dims)`:
   - Stock 240×240 display: **480×480 = 230,400 px (was 345,600 px — a ~33% pixel-count reduction)**.
   - New 320×240 displays: 640×640 = 409,600 px.
   In-code rationale (VERIFIED, `0.8.6:src/seedsigner/views/tools_views.py`): *"Final image will be at least 4x the number of pixels the screen can actually display."* Preview stream simultaneously became `max_dim²` (unchanged 240×240 on stock hardware).

8. **0.8.7 — no chain changes.** Diffs vs 0.8.6 in this path are: `run_screen()` refactor, a "Calculating..." spinner around the (unchanged) chain, and `CameraConnectionError` raised on camera init failure (fail-hard — cannot silently degrade entropy). (VERIFIED by diff.)

**Never changed at any release:** `max_entropy_frames = 50` (VERIFIED identical at every tag 0.4.4→0.8.7); the JPEG encode/decode of the final image (`self._picamera.capture(stream, format='jpeg')` — VERIFIED at 0.4.3, 0.4.4, 0.5.0, and 0.8.7); the CPU-serial and `time.time()` folds and the `hash_bytes = b'0'` serial-failure fallback (verbatim since 0.4.4); preview frames captured as **raw** RGB via `PiRGBArray`/`capture_continuous` — never JPEG (VERIFIED at 0.8.7 `pivideostream.py`).

---

## 4. THE KEY QUESTION — was there ever a genuinely weak period?

**Direct answer: No release ever shipped with a structurally broken entropy source, and no release could produce a seed with zero camera contribution. But v0.4.3 (2021-07-31 → 2021-08-27, one release, ~4 weeks) is materially the leanest version, and the preview-frame layer's held-button bypass (relevant to the v0.8.7 audit) dates to v0.7.0.**

Point by point:

- **Could the camera contribution ever be empty/zero while still producing a seed?** **No, in every release.** The final image is unconditionally hashed last. If the camera fails, `capture_frame()` raises (`Must call start_single_frame_mode first.` / picamera exceptions; from 0.8.7, `CameraConnectionError`) and no seed is produced — a crash/error screen, never a degraded seed. VERIFIED at 0.4.3, 0.4.4, 0.5.0, 0.8.7. There is no code path in any tag that substitutes a default or empty image.

- **Was the preview-frame layer ever the *only* image contribution?** **No, in every release.** The reverse is possible (final image with zero preview frames — see §5) but the final image is always present.

- **Was the final image ever small/quantised enough that entropy could plausibly be marginal vs 256 bits?** **No.** The floor across all releases is 0.8.6/0.8.7's 480×480 = 230,400 RGB pixels (691,200 bytes hashed) from a JPEG-decoded live-scene capture; every earlier release used 720×480 = 345,600 px. A real-world scene at these resolutions carries sensor noise and scene entropy orders of magnitude beyond 256 bits even after JPEG quantisation. **INFERRED** (information-theoretic argument, consistent with the separate empirical measurement on instrumented v0.8.7 hardware); the degenerate case — lens covered, uniform scene — reduces per-pixel entropy substantially and cannot be bounded from code alone. That degenerate case is *worst* in v0.4.3, where the single image was the entire chain; from 0.4.4 onward the (normally ~50) preview frames and, marginally, `time.time()` sub-second jitter provide defense-in-depth.

- **Did any version rely more heavily on CPU serial + `time.time()`?** **No version ever relied on them at all.** v0.4.3 didn't include them; v0.4.4+ added them explicitly as *supplements* ("hardware-level uniqueness," "modest entropy" per the code comments and PR #76). They are near-constant on this hardware (no RTC, no network; VERIFIED premise from audit context) and were never load-bearing in any release: removing them from any version's chain would not change the security argument, which rests on the image(s).

- **12-word truncation:** introduced 0.5.0; uses the first 128 bits of the final digest — standard BIP-39 strength for 12 words, not a defect.

- **Quantified ranking of historical exposure** (weakest first, all VERIFIED code / INFERRED entropy):
  1. **v0.4.3** — single JPEG image, 253 effective digest bits, no supplementary layers. Fine under normal use; no safety net for a degenerate scene. One release, four weeks.
  2. **v0.7.0–v0.8.7** — full chain, but preview layer silently bypassable by a held button (§5); floor = serial + time + final image.
  3. **v0.4.4–v0.6.0** — full chain; preview layer bypass only via a warm-up race (0.4.4–0.4.6) or crash (0.5.0–0.6.0, issue #450).

**A seed generated on any release from v0.4.4 (Aug 2021) onward under normal interactive use (watching the live preview, then clicking) went through the identical chain shipping in v0.8.7 — including a seed generated in 2022 (v0.4.6/0.5.0/0.5.1).** A seed generated on v0.4.3 in July/August 2021 hashed only the single final photo; if it was a photo of a real scene, it is still computationally fine (INFERRED); it simply lacked the later defense-in-depth.

---

## 5. The `check_for_low` early return — when did the shape appear?

**VERIFIED: the return-before-append shape was introduced by commit `91b02061` (2023-08-23), merged as PR #453 (2023-08-24), first released in v0.7.0 (2023-09-04). It has been present in every release since: 0.7.0, 0.8.0, 0.8.5, 0.8.6, 0.8.7. It was NOT always present — v0.4.4 through v0.6.0 appended the current frame *before* checking the button.**

Before (VERIFIED, `0.5.0:src/seedsigner/gui/screens/tools_screens.py`, same order in 0.4.4–0.6.0):

```python
while True:
    frame = self.camera.read_video_stream(as_image=True)
    if frame is not None:
        ...display...
        if len(preview_images) < max_entropy_frames:
            preview_images.append(frame)

    if self.hw_inputs.check_for_low(HardwareButtonsConstants.KEY_LEFT):
        ...
        return RET_CODE__BACK_BUTTON

    elif self.hw_inputs.check_for_low(HardwareButtonsConstants.KEY_PRESS):
        ...
        return preview_images
```

After (VERIFIED, `0.8.7:src/seedsigner/gui/screens/tools_screens.py`, introduced by `91b02061`):

```python
while True:
    if self.hw_inputs.check_for_low(HardwareButtonsConstants.KEY_LEFT):
        ...
        return RET_CODE__BACK_BUTTON

    frame: Image = self.camera.read_video_stream(as_image=True)
    if frame is None:
        time.sleep(0.01)
        continue
    ...
    # Check for ANYCLICK to take final entropy image
    if self.hw_inputs.check_for_low(keys=HardwareButtonsConstants.KEYS__ANYCLICK):
        ...
        return preview_images          # <-- current frame never appended

    ...
    if len(preview_images) == max_entropy_frames:
        preview_images.pop(0)
    preview_images.append(frame)
```

`check_for_low` is a raw GPIO level test (`return self.GPIO.input(key) == self.GPIO.LOW` at 0.4.4; same semantics with multi-key support at 0.8.7 — both VERIFIED), so a **held** button satisfies it on every iteration. Consequences:

- **0.7.0+ :** button held on entry → the loop returns on the *first* iteration that yields a frame, with `preview_images == []`. Downstream, `[] != RET_CODE__BACK_BUTTON` (`1000`, VERIFIED at `0.8.7:src/seedsigner/gui/screens/screen.py:25`) so the flow proceeds, and `for frame in preview_images:` is a silent no-op — **zero chained preview frames**, exactly the v0.8.7 audit observation. A normal click (button not held during preview) loses only the current frame; the previous ≤50 frames are all chained.
- **0.4.4–0.4.6:** append-before-check meant a click could only be recognized in an iteration whose frame had already been appended — *except* during the camera warm-up window when `frame is None`, where a held button could break out with zero frames (race; no crash because the 0.4.4 press-branch doesn't touch `frame`).
- **0.5.0–0.6.0:** same race, but the press-branch does `self.renderer.canvas.paste(frame)` with `frame = None`, which **crashes** (`ValueError: cannot determine region size; use 4-item box`) instead of producing a seed — this is precisely **issue #450** (VERIFIED from the issue's traceback: `tools_screens.py line 68, in _run: self.renderer.canvas.paste(frame)`).

So the precise regression statement: **PR #453 (v0.7.0) converted a crash-on-race into a silent zero-preview-frame path, and made that path reachable deterministically by holding a button (any of four buttons after v0.8.5's ANYCLICK change), not just by winning a warm-up race.** The same PR *improved* normal-use entropy by keeping the *last* 50 frames (closest to the click, after the user has framed a scene) instead of the *first* 50 (camera warm-up, ~2s after entering the screen, potentially before the user aimed at anything). Neither effect was called out as entropy-relevant in the PR — the discussion is entirely about the PIL crash.

Mitigating context (all releases): even with zero preview frames, the final 480×480/720×480 image is always hashed, so the held-button path degrades to roughly the v0.4.3 posture (plus serial/time) rather than to a deterministic seed.

## 6. Other notable items

- **Serial-read fallback** (`except: hash_bytes = b'0'`, 0.4.4→0.8.7): silently substitutes a constant if `/proc/cpuinfo` parsing fails. Not a real weakening — the serial is a uniqueness salt, not secret entropy — but it is a silent-degrade pattern worth noting.
- **`str(time.time())`**: float string with µs digits; on RTC-less hardware the integer part is boot-predictable, sub-second digits contribute modest user-timing jitter (INFERRED, ~10–20 bits at best). Comment calls it "modest entropy" — accurately.
- **Memory hygiene**: since 0.4.4 the code nulls `seed_entropy_image` / `preview_images` / hashes after use (`# Image should never get saved nor stick around in memory`), but Python `None`-assignment does not scrub buffers. Buffer-scrubbing work exists only in unreleased LVGL-migration branches (`23de1fb5` "fix(entropy): scrub the camera buffers holding seed material") — not in any release through 0.8.7.
- **Test coverage**: `e7dd69b0` (2023-03-03) added unit tests for `mnemonic_generation` byte→mnemonic conversion only; the image-entropy chain composition itself has never had release-tagged test coverage (VERIFIED: tests target `generate_mnemonic_from_bytes`, not the chain).
- **Could not determine**: the actual min-entropy of a JPEG-decoded degenerate (lens-covered) frame per firmware version — settling it requires empirical capture on hardware per release image (only v0.8.7 was measured; see the analysis's data and methodology document).

---

## Amendment 2026-08-07 (adversarial review): the 720×480 column is capture geometry, not scene content

From 0.4.5 through 0.8.5 the hashed final is the CAPTURED 720×480 buffer after
`Image.open(stream).rotate(90 + rotation)` with default rotation 0. PIL `rotate(90)` without
`expand` keeps the 720×480 canvas, so the hashed buffer is a 480×480 scene region plus one
third constant-black fill (115,200 of 345,600 pixels; verified empirically), with a third of
the scene columns cropped away — the era's own display crop `(120, 0, 600, 480)` frames
exactly the live region. Consequences: (1) "rotation permutes pixels" is true only for square
frames (previews; finals from 0.8.6); (2) only 0.4.3/0.4.4 hashed a genuinely larger scene
area than today's 480×480 — from 0.4.5 the scene content equals the current configuration,
plus a constant fill that contributes nothing to entropy.
