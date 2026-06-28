# STYLE.md — the drafting-paper blueprint design system (v3, current)

What every visual element MEANS, so the look stays consistent and any change is deliberate.
Values live in `scripts/tokens.py` (the single source of truth — never hardcode style
elsewhere); the app shell lives in `scripts/assets/` (app.css/app.js/page.html). This doc is
the legend behind the legend, kept in sync with the implementation.

## App shell (Geist/Vercel-style grid)
- **One fixed-viewport frame:** a clean header bar on top, the active diagram below. Only the
  diagram body scrolls — there is no page scroll, so a big diagram never fights nested scrolls.
- **Header** — one uncluttered bar (no inner vertical dividers; only the bottom hairline, which
  lines up with the diagram grid): `# Blueprint · <project> / <scenario ▾> · N scenarios`.
- **Scenario switcher** — with 2+ scenarios the active title is a **dropdown** (▾) listing all
  scenarios; pick one to swap the panel. One scenario → plain text, no dropdown. `↑/↓`/`j/k` cycle.
- **Toolbar** (bottom) — a row of border-divided cells: the colour-lens toggles, the active
  lens's legend, and the ⤓ PNG export (in-browser canvas stitch of header + body).

## Surface
- **Paper** (`PAPER`, warm cream) — the canvas. A single faint **grid** (`HAIRLINE` at `GRID`
  pitch) reads as engineering paper. Pure texture, never load-bearing.
- **Zebra** (`ZEBRA`, barely-there neutral) — alternate actor lanes get a faint tonal band so the
  eye tracks columns. Tone, not colour — identity is carried by header position + the bar colour.

## Structure
- **Lifelines** — strong dotted vertical (`LIFELINE`). A participant's existence over time.
- **Activation bars** — thin, **solid in the column's positional identity colour** (matches its
  header), darker stroke for a crisp edge. A participant is busy / on the call stack. Bars are the
  identity-by-colour channel and are **never lens-coloured** (lenses only touch message arrows), so
  identity stays constant across every lens. (`BAR_HALF`, colour via `bar_colors`/`category`.)
- **Header band** — one continuous divided grid, two tiers: actor (tier-1, in its category hue)
  over its sub-services (tier-2, in lightness-shades of that hue). `GROUP_DIV` between actors.
- **Left phase rail** — a narrow column of vertical `{phase}` labels with solid `PHASE_DIV`
  boundaries spanning the width; chunks a long flow into sections.

## Colour = a generated, adaptive palette (positional, not semantic)
- Each top-level actor gets an **even-spaced OKLCH hue** at a tuned lightness/chroma (`PAL_L`,
  `PAL_C`), skipping the muddy yellow→green arc, so any project's services come out maximally
  separated and equally vivid — and it adapts to any number of actors. The human `user` actor is a
  warm neutral (`NEUTRAL`). Colour is **positional, not fixed** (Firebase isn't "always amber").
- Each **sub-service** is a lightness step of its parent's hue (`sub_color`, the Tableau-20 idiom):
  kin from afar, separable up close.

## Messages (mechanics = line style + arrowhead; category = a drawn marker; NEVER colour)
- **Sync call** — solid line, filled triangle head. **Return** — dashed line, open chevron.
  **Async / event** — solid line, OPEN chevron (the UML async message). That's the mechanics channel.
- **Type marker** — a tiny DRAWN shape (never a font glyph, so the deterministic monospace width math
  holds) sitting just left of the primary label, for the two categories the arrowheads can't express:
  `api` = double chevron (crosses a process/network boundary) · `io` = cylinder (a data store). A plain
  in-process call (`fn`) gets NO marker. Markers are soft-ink, follow the message on hover-dim /
  path-accent, and are keyed off in the toolbar legend so a static PNG self-documents.
- **Self-call** — a small loop on the lifeline (= an on-device process); text on whichever side has room.
- **Note** — a folded-page ICON + a short tag on the lifeline; an aside, not a message. The full text
  and any `src` open in the click popover, so a caveat never crowds the canvas. Genuine caveats only.
- **Label** — a bold PRIMARY line above the arrow (one short clause, ellipsised to fit) + an optional
  soft SECONDARY caption below it (params / state / detail). Arrow + self labels do NOT wrap — overflow
  ellipsises and reveals in full on click; notes keep their box wrap. No opaque plate.

## Lenses = one switchable overlay at a time (the only place colour means a variable)
Neutral by default; at most ONE lens active; each ships an auto-legend. Lenses recolour/dim
**message arrows only** — bars keep their identity colour.
- **`path-<name>`** — light one named flow in the **accent** (`ACCENT`, oxblood), dim the rest.
- **`cost` / `lat` (metric)** — a **hueless graphite ramp** (`METRIC_RAMP`, pale→near-black ink):
  magnitude reads as ink density, so it can never be mistaken for a categorical hue now that bars
  use the whole wheel. Lights only messages carrying that metric; absent data → lens not offered.

Cardinal rule: **never spend the colour channel on two meanings at once.** Mechanics → line style +
arrowhead (UML); category → a drawn marker; identity → bar/header hue (positional); a *variable* → a
lens with a legend. Colour never carries kind.

## Typography
Monospace everywhere (`MONO`) — technical, even, and gives exact text metrics so layout is
deterministic without a font-measuring dependency. Weight + size carry hierarchy; colour does not.

## The one-line rule
Reaching for a new colour? Stop: is it structure (→ neutral/zebra), mechanics (→ line style +
arrowhead), category (→ a drawn marker), identity (→ the positional hue), or a *new variable* (→ a lens
with a legend)? There is no sixth reason.
