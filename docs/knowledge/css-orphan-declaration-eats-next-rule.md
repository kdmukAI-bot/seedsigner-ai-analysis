# A stray declaration in a `<style>` block silently deletes the rule after it

Found in `dice/standard.html`, where two working style rules had stopped applying and nothing in
the page looked wrong enough to investigate. The failure is silent, survives copy-paste, and is
invisible to every "is my CSS valid" instinct that relies on reading the rule you care about.

## Symptom

A rule that is plainly present in the stylesheet has no effect. In this case `.checkline` (the
"check this method yourself" line under each method heading) and `nav.toc .tocnote` both rendered
unstyled, while the rules sat right there in the `<style>` block, correctly spelled, with valid
properties and matching elements in the document.

## Cause

Editing a `<style>` block by hand — deleting a rule's selector and opening brace but leaving its
declarations behind — produces this:

```css
.wlist sup{ font-size:.62rem; }
  border-bottom:1px solid var(--rule); align-items:baseline}   /* orphan */
.checkline{ border-left:2px solid var(--accent); }             /* never applies */
```

CSS error recovery is not "skip the bad line." Per the CSS Syntax spec, when the parser hits
something that is not a valid rule start at the top level, it *consumes a qualified rule*: it keeps
appending tokens to a prelude until it finds a `{ }` block, then discards the whole thing as an
invalid selector. A stray `}` at the top level is consumed as just another prelude token, not as a
terminator.

So the parser swallows the orphan declarations **and the next real rule's selector**, then treats
that rule's body as the block belonging to a garbage prelude, and throws all of it away. One orphan
fragment costs you the rule that follows it — never the one before, which is why reading upward
from the broken rule finds nothing wrong.

Three orphan fragments in this file killed two rules; the third landed before a comment and cost
nothing, which is part of why it went unnoticed.

## Why it is easy to miss

- The dead rule is syntactically perfect. Linting it in isolation passes.
- Browser devtools show the rule as simply absent, not as an error — it was discarded at parse time.
- The visual result is "slightly plain", not "broken". A missing left border and a font-size revert
  read as a design choice.
- The damage is positional: it hits whatever rule happens to be next, so an unrelated edit
  elsewhere can appear to fix or cause it.

## Detection

Balance-check the block rather than reading it. Walk the `<style>` contents tracking brace depth
and collect any text that appears at depth 0 outside a selector position:

```python
css = html[html.index('<style>')+7 : html.index('</style>')]
depth, buf, i = 0, '', 0
while i < len(css):
    if css.startswith('/*', i):
        i = css.index('*/', i) + 2; continue
    c = css[i]
    if c == '{':
        if depth == 0: buf = ''
        depth += 1
    elif c == '}':
        depth -= 1
        if depth == 0: buf = ''
    elif depth == 0:
        buf += c
    i += 1
assert not buf.strip(), f'stray top-level CSS: {buf.strip()[:80]!r}'
```

Anything left in `buf` at the end is an orphan fragment, and the rule immediately after it is the
one currently being eaten. This runs in milliseconds and belongs in whatever pre-publish check the
page already has.

## Related

- `rotated-table-headers-hit-area.md` — the other CSS failure in this page that presents as
  something else entirely (there, "flaky links" rather than "plain text").
