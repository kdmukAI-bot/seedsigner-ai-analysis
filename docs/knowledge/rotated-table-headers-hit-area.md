# Angled table headers: the clickable area is not where the text is

Applies to `dice/standard.html`'s implementation matrix, and to any table using diagonal column
labels. The symptom is easy to misread as "the links are flaky".

## Symptom

Clicking or hovering an angled column heading activates the *wrong* column, and the error grows the
further up the diagonal you point. Near the top-right end of a label, the column that responds can
be two columns to the right of the text under the cursor.

## Cause

The usual way to build angled headers keeps the cell narrow so the rotated label cannot widen the
column:

```css
.mx th.rot a   { display:block; width:3.1rem; height:9.4rem; position:relative }
.mx th.rot span{ position:absolute; bottom:.3rem; left:50%;
                 transform-origin:left bottom; transform:rotate(-45deg) }
```

The anchor keeps an **unrotated** box: a tall, narrow vertical strip filling its own column. The
label is absolutely positioned and rotated *out* of that strip, flying up and to the right across
its neighbours.

Both are hit-testable, so the pointer area is the union of a diagonal label and a vertical strip
that has nothing to do with it. Where a label overlaps a neighbouring column's strip, the later
sibling paints on top and takes the pointer. The higher up the diagonal, the further right the strip
you are actually over.

## Fix

Take the pointer away from the anchor's layout box and give it to the visible label:

```css
.mx th.rot a   { pointer-events:none }
.mx th.rot span{ pointer-events:auto; cursor:pointer }
```

The click still works: the event target is the span, and it bubbles through the anchor, so default
activation and `:hover` on the anchor both still fire (hover state propagates to ancestors).
`pointer-events` does not affect focus, so keyboard navigation is untouched.

## Residual

Adjacent labels still overlap slightly at their tails, where the later sibling wins. That is
inherent to diagonal labels; it is now a few pixels rather than a full column height.

Leave a comment at the CSS, because `pointer-events:none` on an anchor reads as a mistake to anyone
who has not seen the bug.
