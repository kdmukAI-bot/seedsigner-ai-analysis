# Figures

## The social cards for `dice/standard.html`

| File | Theme | Use |
|---|---|---|
| `social-card.jpg` | Dark | The shipped `og:image`. Holds up better at preview size. |
| `social-card-light.jpg` | Light | Alternate, kept for contexts that want the paper look. |

Both are rendered from the single source `social-card.html` rather than drawn, so they use the
page's own type and color tokens (`assets/fonts.css`, `assets/series.css`) and cannot drift from
them or from each other. Nothing in them is invented: the dice, the digest and the words are the
worked example from [§8, "Hash the rolls as typed"](../standard.html#hash), and the digest
recomputes from the roll string there.

Theme comes from a query parameter, defaulting to light when the file is opened directly, so the
capture never depends on the renderer's color-scheme default.

### Regenerating

Any headless Chromium works. Render at 2x and downsample, which is noticeably sharper than
rendering at 1x:

```bash
cd dice/figures
B=chromium   # or a playwright headless_shell binary

# dark (the shipped card)
$B --headless --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=2 --window-size=1200,630 \
  --screenshot=/tmp/dark.png "file://$PWD/social-card.html?theme=dark"

# light (the alternate)
$B --headless --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=2 --window-size=1200,630 \
  --screenshot=/tmp/light.png "file://$PWD/social-card.html"

python3 -c "
from PIL import Image
Image.open('/tmp/dark.png').convert('RGB').resize((1200,630), Image.LANCZOS).save(
    'social-card.jpg', quality=94, optimize=True, progressive=True)
Image.open('/tmp/light.png').convert('RGB').resize((1200,630), Image.LANCZOS).save(
    'social-card-light.jpg', quality=92, optimize=True, progressive=True)"
```

1200x630 is the Open Graph size the `<meta>` tags declare, and matches
`image-entropy/figures/social_card.jpg`. The dark card is saved a little higher quality because
flat dark grounds band more visibly under JPEG.

If you switch which card ships, change the `og:image` and `twitter:image` URLs in
`dice/standard.html` to match. The alt text describes the content rather than the colors, so it
stays correct either way.

### Constraints worth preserving

- **It is mostly seen small, and X is the smallest case.** Previews render a few hundred pixels
  wide, so a 1200px-wide card is being shown at roughly a third of its size. Check any edit at
  **~400px wide**, not at full size.
- **Nothing on the card is set below 19px.** At X's scale that is already only ~6px on screen.
  Type smaller than that is not small text, it is noise: it costs legibility everywhere and buys
  nothing, because nobody can read it at any size the card actually appears. The first draft used
  13px beat labels and a 15px eyebrow, which disappeared entirely. If a line is not worth 19px,
  cut it instead of shrinking it.
- The digest is the deliberate exception: it reads as texture by design, standing for "a hash"
  rather than asking to be read.
- **The three beats share one fixed-height band** (`.bc`), so their labels land on a single
  baseline and the arrows land on the content's optical center. Sizing each beat to its own
  content instead leaves the labels ragged and the arrows floating above the dice.
