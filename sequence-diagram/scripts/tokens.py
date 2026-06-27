"""Design tokens — the single source of truth for the v3 'drafting-paper blueprint'
look (DESIGN-v3 decision 11). Pure data, no logic. The renderer reads these; callers
never touch style, so the look stays frozen + identical every run.

See STYLE.md for what each element/colour MEANS.
"""
import math

# ── paper + ink ───────────────────────────────────────────────────────────────
PAPER       = "#F3EEE1"   # warm drafting-paper cream
INK         = "#21201B"   # near-black warm ink (text, arrowheads)
INK_SOFT    = "#6B6657"   # secondary text (subtitles, sub-labels, meta)
HAIRLINE    = "#211E1408" # faint grid line (rgba via 8-hex alpha)
LIFELINE    = "#897D58"   # dotted lifeline colour (strong contrast vs paper)
RULE        = "#C6BDA3"   # header dividers / frame borders
HEADER_BG   = "#E7DEC8"   # header band fill (distinct from paper)
ZEBRA       = "#7B73560F" # alternate-lane neutral band (no colour, just tone)
GROUP_DIV   = "#B4AA8C"   # vertical divider between actor sections (stronger)
PHASE_DIV   = "#9E9173"   # horizontal phase boundary — solid, medium weight (bolder than the lifelines)
RAIL        = "#E6DECA"   # left phase-index rail fill (reads as a column)
FRAME_COL   = "#8A7E5C"   # combined-fragment border — neutral khaki-grey, DASHED: a container, never
                          # confused with a message line or a (possibly teal) actor's identity colour
FRAME_TAB   = "#E2D9C0"   # fragment label-tab fill (light neutral)
# activation bars + headers pull from the generated OKLCH palette below (positional, adaptive)

ACCENT      = "#B23A2E"   # THE single reserved accent (path-highlight). Oxblood red.

GRID        = 23          # grid pitch (px) — single faint level

# ── type ──────────────────────────────────────────────────────────────────────
MONO = "'JetBrains Mono','SF Mono',ui-monospace,'Menlo','DejaVu Sans Mono',monospace"
FS_BAND    = 12          # actor (tier-1) header label
FS_SUBBAND = 10.5        # sub-service (tier-2) header label
FS_MSG     = 9.5         # message PRIMARY label (the one short line that rides the arrow)
FS_CAP     = 8.5         # message SECONDARY label (the demoted soft caption under the primary)
FS_NOTE    = 9.5
CH = 0.605               # monospace advance width as a fraction of font-size

# ── type markers (drawn as SVG, NOT font glyphs — so width math stays deterministic) ──
# Only the two categories UML's arrowheads can't express get a marker; fn = no marker.
MARKER_R   = 3.4         # marker half-size (px)
MARKER_PAD = 8           # gap from the marker centre to the primary label's left edge
NOTE_ICON_W = 8          # collapsed-note folded-page glyph width (full text + src open on click)
PRIMARY_MAXCH = 30       # soft cap on the primary label (validator WARNS past this)
CAP_MAXCH     = 36       # soft cap on the caption

# ── layout geometry (css px) ──────────────────────────────────────────────────
COLW       = 146         # MIN lifeline column width; widens to fill FILL_W so the diagram is full-bleed
FILL_W     = 1380        # target full-bleed canvas width — columns SPREAD to fill this, so every
                         # scenario is full-width at ONE consistent scale (fonts never change with
                         # column count; sparse diagrams stop leaving blank space on the right)
FILL_H     = 860         # target canvas height — lifelines/grid/rail extend to fill when a scenario
                         # is short (CSS tiles the grid past this for taller viewports, so no blank band)
RAIL_W     = 30          # left phase-index rail width
TIER1_H    = 23          # actor band height
TIER2_H    = 19          # sub-service band height
HEAD_TOP   = 0           # header band fills the svg flush (no padding); CSS borders divide sections
ROW        = 38          # vertical pitch between messages (room for an optional 2nd caption line)
ROW_TOP    = 10          # gap from lifeline top to first message
PHASE_GAP  = 26          # extra air inserted at a {phase} marker
PHASE_LEAD = 32          # healthy top padding BELOW a phase line, before its first message
BAR_HALF   = 3           # activation-bar half-width (thin → reads as a crisp solid service tick)
LINE_H     = 12.5        # wrapped-line height
FRAME_PAD  = 13          # combined-fragment frame side padding
FRAME_TOP  = 20          # extra air before a fragment's first row (room for its label tab + a caption above)

# ── generated categorical palette (OKLCH — perceptual, adaptive) ───────────────
# Identity colour is POSITIONAL, not semantic: each top-level actor gets an even-spaced
# hue, so a project with any number of services comes out maximally separated and equally
# vivid. Hues skip the muddy yellow→green arc. Sub-services are lightness steps of the
# parent hue (the Tableau-20 idiom). The human "user" actor stays a warm neutral.
PAL_L      = 0.62        # base lightness — visible on cream, never too dark
PAL_C      = 0.125       # base chroma — balanced: colourful yet premium
SUB_SPAN   = 0.14        # total lightness spread across a category's sub-services
_HUE_START = 150.0       # usable hue arc starts after the green band …
_HUE_SPAN  = 270.0       # … spanning 270° (skips ~60–150° yellow/olive/green)

def _l2s(c):
    c = 0.0 if c < 0 else 1.0 if c > 1 else c
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055

def oklch_hex(L, C, Hdeg):
    """OKLCH → sRGB hex (Ottosson constants; pure math, no dependency)."""
    h = math.radians(Hdeg); a = C * math.cos(h); b = C * math.sin(h)
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    r  =  4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g  = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(255 * _l2s(v)))) for v in (r, g, bl))

def darken(h, k=0.72):
    """Multiply an #rrggbb toward black by k — used for a crisp bar/edge stroke."""
    return "#%02X%02X%02X" % tuple(round(v * k) for v in _hex(h))

def cat_hue(i, n):
    """Hue (deg) for category i of n, centred within even sub-arcs of the usable span."""
    return (_HUE_START + _HUE_SPAN * (i + 0.5) / max(1, n)) % 360.0

def category_color(i, n):
    """Base identity colour for hued category i of n."""
    return oklch_hex(PAL_L, PAL_C, cat_hue(i, n))

def sub_color(i, n, j, k):
    """Colour for sub-service j of k inside category i — same hue, stepped lightness."""
    if k <= 1:
        return category_color(i, n)
    L = PAL_L + SUB_SPAN / 2 - SUB_SPAN * j / (k - 1)     # lightest first → darkest last
    return oklch_hex(L, PAL_C, cat_hue(i, n))

NEUTRAL = oklch_hex(0.64, 0.018, 80)     # warm-grey anchor for the human "user" actor

# ── metric-lens sequential scale — hueless graphite (warm-grey → near-black ink).
# Magnitude reads as INK DENSITY, so it can never be mistaken for a categorical hue now
# that the bars span the whole wheel. pale → deep == low → high. ──────────────
METRIC_RAMP = ["#D9D2C4", "#ABA493", "#7C7666", "#4E493D", "#262320"]

def metric_color(t):
    """t in [0,1] → hex on the sequential ramp (linear-interp between stops)."""
    t = 0.0 if t < 0 else 1.0 if t > 1 else t
    n = len(METRIC_RAMP) - 1
    i = min(int(t * n), n - 1)
    f = t * n - i
    a = _hex(METRIC_RAMP[i]); b = _hex(METRIC_RAMP[i + 1])
    return "#%02X%02X%02X" % tuple(round(a[k] + (b[k] - a[k]) * f) for k in range(3))

def _hex(h):
    h = h.lstrip("#")
    return [int(h[k:k + 2], 16) for k in (0, 2, 4)]

def text_w(s, fs):
    """Deterministic monospace text width (px). Exact enough for layout."""
    return len(s) * fs * CH
