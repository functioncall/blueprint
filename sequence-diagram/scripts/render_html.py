#!/usr/bin/env python3
"""v3 renderer: spec JSON -> ONE self-contained interactive index.html.
Drafting-paper blueprint look; swimlane headers; generated OKLCH palette; left phase rail;
service-coloured activation bars; combined fragments; switchable colour LENSES (path / metric)
with auto-legend; grid app-shell with a scenario dropdown; hover-dim; click-detail; WAAPI
entrance; in-browser PNG export. Author writes only JSON; style is frozen in tokens.py +
assets/ + this emitter. Design legend: STYLE.md.

Usage:
  python3 render_html.py <spec.json> [out.html]
A spec may be a single scenario {actors,messages,...} or a master {scenarios:[...]}.
"""
import html
import json
import os
import sys

import tokens as T
import layout as L

# ── tiny SVG helpers (base look via presentation attributes -> PNG-faithful) ──
def esc(s):
    return html.escape(str(s), quote=True)

def _ln(x0, y0, x1, y1, stroke, w=1.0, dash=None, cls="", extra=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    c = f' class="{cls}"' if cls else ""
    return (f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" '
            f'stroke="{stroke}" stroke-width="{w}"{d}{c}{extra}/>')

def _rect(x, y, w, h, fill, stroke="none", sw=1.0, rx=0, dash=None, cls="", extra=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    c = f' class="{cls}"' if cls else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}{c}{extra}/>')

def _txt(x, y, s, fs, fill=T.INK, anchor="middle", weight="400", cls="", extra=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{T.MONO}" font-size="{fs}" '
            f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" '
            f'dominant-baseline="middle"{c}{extra}>{esc(s)}</text>')

def _arrowhead(x, y, right, color, filled=True):
    dx = -8 if right else 8
    if filled:
        return (f'<path d="M{x:.1f},{y:.1f} L{x+dx:.1f},{y-4:.1f} L{x+dx:.1f},{y+4:.1f} Z" '
                f'fill="{color}" class="ah"/>')
    return (f'<path d="M{x+dx:.1f},{y-4:.1f} L{x:.1f},{y:.1f} L{x+dx:.1f},{y+4:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="1.3" class="ah"/>')

def _marker(kind, cx, cy):
    """Tiny SVG type-marker (DRAWN, never a font glyph → deterministic width, no tofu).
    Only the two categories UML arrowheads can't express get one:
    api = double chevron (crosses a process/network boundary); io = cylinder (a data store)."""
    r = T.MARKER_R
    if kind == "api":
        return (f'<g class="tmark">'
                f'<path d="M{cx-r:.1f},{cy-r:.1f} L{cx-1:.1f},{cy:.1f} L{cx-r:.1f},{cy+r:.1f}" '
                f'fill="none" stroke="{T.INK_SOFT}" stroke-width="1.2"/>'
                f'<path d="M{cx+1:.1f},{cy-r:.1f} L{cx+r+1:.1f},{cy:.1f} L{cx+1:.1f},{cy+r:.1f}" '
                f'fill="none" stroke="{T.INK_SOFT}" stroke-width="1.2"/></g>')
    if kind == "io":                                   # cylinder: top ellipse + body
        rx, ry = r, r * 0.42
        top, bot = cy - r * 0.8, cy + r * 0.7
        return (f'<g class="tmark">'
                f'<path d="M{cx-rx:.1f},{top:.1f} V{bot:.1f} '
                f'A{rx:.1f},{ry:.1f} 0 0 0 {cx+rx:.1f},{bot:.1f} V{top:.1f}" '
                f'fill="none" stroke="{T.INK_SOFT}" stroke-width="1.1"/>'
                f'<ellipse cx="{cx:.1f}" cy="{top:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
                f'fill="none" stroke="{T.INK_SOFT}" stroke-width="1.1"/></g>')
    return ""

def _note_icon(cx, cy):
    """Tiny folded-corner page glyph — a COLLAPSED note. The short tag rides beside it;
    the full text + any src open in the click popover, so a note never crowds the canvas."""
    w, h, f = T.NOTE_ICON_W, 9, 3
    x, yt = cx - w / 2, cy - h / 2
    return (f'<g class="tmark">'
            f'<path d="M{x:.1f},{yt:.1f} h{w-f:.1f} l{f},{f} v{h-f:.1f} h{-w:.1f} Z" '
            f'fill="none" stroke="{T.INK_SOFT}" stroke-width="1.1"/>'
            f'<path d="M{x+w-f:.1f},{yt:.1f} v{f} h{f}" fill="none" stroke="{T.INK_SOFT}" stroke-width="1.1"/></g>')


def _fill_bg(g):
    """Per-card tiling background so the dotted lifelines + grid CONTINUE into any space below a
    short diagram — the canvas never ends in a blank band. The body svg's opaque paper covers this
    inside the diagram; it shows only in the gap. Width-relative (%), so the lifelines stay aligned."""
    W = g["width"]
    lines = "".join(
        f"<line x1='{c['x']:.1f}' y1='0' x2='{c['x']:.1f}' y2='10' "
        f"stroke='{T.LIFELINE}' stroke-width='1.4' stroke-dasharray='1.5 3.5'/>" for c in g["cols"])
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' preserveAspectRatio='none' "
           f"viewBox='0 0 {W:.0f} 10'>{lines}</svg>")
    enc = (svg.replace('%', '%25').replace('#', '%23').replace('<', '%3C')
              .replace('>', '%3E').replace(' ', '%20').replace("'", '%27'))
    return (f"background-image:url('data:image/svg+xml,{enc}'),"
            f"linear-gradient(var(--grid) 1px,transparent 1px),"
            f"linear-gradient(90deg,var(--grid) 1px,transparent 1px);"
            f"background-size:100% 10px,23px 23px,23px 23px;"
            f"background-repeat:repeat-y,repeat,repeat;")

# ── per-scenario SVG ──────────────────────────────────────────────────────────
def emit_header(g, sid):
    """The swimlane header — its own SVG so it can stay pinned while the body scrolls.
    One grid: cells filled edge-to-edge, single internal dividers, NO self-stroke
    (section boundaries are the CSS borders; actor verticals align with the body)."""
    W, HR, hh, two, hdr2 = g["width"], g["head_region"], g["head_h"], g["two_tier"], g["hdr2"]
    colw = g["colw"]
    groups = g["groups"]
    p = [f'<svg class="seqhead" viewBox="0 0 {W} {HR}" width="{W}" height="{HR}" '
         f'preserveAspectRatio="xMinYMin meet" xmlns="http://www.w3.org/2000/svg" font-family="{T.MONO}">',
         _rect(0, 0, T.RAIL_W, HR, T.RAIL),                       # rail cell, flush
         _rect(T.RAIL_W, 0, W - T.RAIL_W, HR, T.HEADER_BG),       # header band, flush edge-to-edge
         _ln(T.RAIL_W, 0, T.RAIL_W, HR, T.GROUP_DIV, 1.0)]        # rail │ content (single)
    if two:
        p.append(_ln(T.RAIL_W, T.TIER1_H, W, T.TIER1_H, T.RULE, 1.0))   # tier divider (single)
    y_t1, y_t2 = T.TIER1_H / 2, T.TIER1_H + T.TIER2_H / 2
    for i, grp in enumerate(groups):
        if i > 0:                                                 # actor divider — full height, aligns w/ body
            p.append(_ln(grp["x0"], 0, grp["x0"], HR, T.GROUP_DIV, 1.1))
        p.append(_txt(grp["cx"], y_t1 if hdr2 else hh / 2, grp["parent"],
                      T.FS_BAND, T.darken(grp["lblcol"], 0.88), weight="700"))
        if grp["subs"]:
            for j, sub in enumerate(grp["subs"]):
                if j > 0:                                         # sub-column divider — tier-2 only
                    p.append(_ln(sub["x"] - colw/2, T.TIER1_H, sub["x"] - colw/2, HR, T.GROUP_DIV, 0.8))
                p.append(_txt(sub["x"], y_t2, sub["label"], T.FS_SUBBAND, T.darken(sub["color"], 0.78), weight="600"))
        elif grp["subcap"]:
            p.append(_txt(grp["cx"], y_t2 if hdr2 else hh - 7, grp["subcap"],
                          T.FS_SUBBAND - 0.5, T.INK_SOFT))
    p.append("</svg>")
    return "".join(p)


def emit_body(g, sid):
    """Everything below the header — scrolls inside the card."""
    W, HR, H = g["width"], g["head_region"], g["height"]
    BH = H - HR
    life_top, life_bot, groups = g["life_top"], g["life_bot"], g["groups"]
    p = [f'<svg class="seqbody" viewBox="0 {HR} {W} {BH}" width="{W}" height="{BH}" '
         f'preserveAspectRatio="xMinYMin meet" xmlns="http://www.w3.org/2000/svg" font-family="{T.MONO}">',
         f'''<defs><pattern id="grid-{sid}" width="{T.GRID}" height="{T.GRID}" patternUnits="userSpaceOnUse">
           <path d="M {T.GRID} 0 L 0 0 0 {T.GRID}" fill="none" stroke="{T.HAIRLINE}" stroke-width="1"/></pattern></defs>''',
         _rect(0, HR, W, BH, T.PAPER), _rect(0, HR, W, BH, f"url(#grid-{sid})")]

    # neutral zebra bands (alternate lanes) + subtle group dividers
    for i, grp in enumerate(groups):
        if i % 2 == 1:
            p.append(_rect(grp["x0"], life_top, grp["x1"] - grp["x0"], life_bot - life_top, T.ZEBRA))
        if i > 0:
            p.append(_ln(grp["x0"], life_top, grp["x0"], life_bot, T.GROUP_DIV, 1.0))
    # lifelines (strong dotted, high contrast)
    for c in g["cols"]:
        p.append(_ln(c["x"], life_top, c["x"], life_bot, T.LIFELINE, 1.4, dash="1.5 3.5"))
    # left phase-index rail: bands with vertical labels + faint full-width boundary ticks
    p.append(_rect(0, life_top, T.RAIL_W, life_bot - life_top, T.RAIL))
    p.append(_ln(T.RAIL_W, life_top, T.RAIL_W, life_bot, T.GROUP_DIV, 1.0))
    for k, bd in enumerate(g["bands"]):
        if k > 0 and bd["border"]:                   # solid medium phase boundary (skipped for an empty band)
            p.append(_ln(0, bd["y0"], groups[-1]["x1"], bd["y0"], T.PHASE_DIV, 1.3))
        if bd["label"]:                              # empty band → label near its top (nice spacing, no border)
            cyb = bd["y0"] + 26 if not bd["border"] else (bd["y0"] + bd["y1"]) / 2
            p.append(_txt(T.RAIL_W / 2, cyb, bd["label"], 9.5, T.INK_SOFT, weight="700",
                          extra=f' transform="rotate(-90 {T.RAIL_W/2:.1f} {cyb:.1f})"'))
    # combined-fragment frames (behind messages)
    for fr in g["frames"]:
        p.append(_rect(fr["x0"], fr["y0"], fr["x1"] - fr["x0"], fr["y1"] - fr["y0"],
                       "none", T.FRAME_COL, 1.3, rx=3, dash="6 4", cls="frame"))
        tabw = T.text_w(fr["kind"], 10) + 14
        p.append(_rect(fr["x0"], fr["y0"], tabw, 15, T.FRAME_TAB, T.FRAME_COL, 1.2, rx=2))
        p.append(_txt(fr["x0"] + tabw/2, fr["y0"] + 8, fr["kind"], 10, T.FRAME_COL, weight="700"))
        if fr["label"]:
            p.append(_txt(fr["x0"] + tabw + 7, fr["y0"] + 8, f'[{fr["label"]}]', 10,
                          T.FRAME_COL, anchor="start"))
        for dv in fr["divs"]:
            p.append(_ln(fr["x0"], dv["y"], fr["x1"], dv["y"], T.FRAME_COL, 1.0, dash="5 4"))
            if dv["guard"]:
                p.append(_txt(fr["x0"] + 8, dv["y"] + 11, f'[{dv["guard"]}]', 10, T.FRAME_COL, anchor="start"))
    # activation bars — thin, solid in the column's positional identity colour (matches its header)
    for b in g["bars"]:
        fill = g["cols"][b["ci"]]["color"]
        p.append(_rect(b["x"] - T.BAR_HALF, b["y0"], 2 * T.BAR_HALF, b["y1"] - b["y0"],
                       fill, T.darken(fill), 0.8, rx=1.5, cls="bar"))
    for i, m in enumerate(g["messages"]):
        p.append(_emit_message(i, m))
    p.append("</svg>")
    return "".join(p)


def _emit_message(i, m):
    paths = m.get("paths", [])
    metrics = m.get("metrics", {})
    cls = ["msg"]
    style = [f"--d:{min(i * 0.028, 0.42):.3f}s"]   # capped stagger — snappy on long diagrams
    for pa in paths:
        cls.append("p-" + _slug(pa))
    if "cost" in metrics:
        cls.append("has-cost"); style.append(f'--c-cost:{m["_ccost"]}')
    if "latency_ms" in metrics:
        cls.append("has-lat"); style.append(f'--c-lat:{m["_clat"]}')
    data = f' data-full="{esc(m["text"])}"'
    if m["type"] in ("note", "self"):              # content-led card (the label IS the substance)
        data += f' data-type="{m["type"]}"'
    # deterministic header (computed in layout): readable route, position, phase, fragment guard
    for k in ("route", "phase", "frag"):
        if m.get(k):
            data += f' data-{k}="{esc(m[k])}"'
    if m.get("step"):
        data += f' data-step="{esc(str(m["step"]))}/{esc(str(m.get("total", m["step"])))}"'
    # AI-prefilled detail (architecture.json) — every key optional, omitted when absent
    det = m.get("detail") or {}
    for k in ("why", "sends", "effects", "fails", "ordering", "auth"):
        if det.get(k):
            data += f' data-{k}="{esc(det[k])}"'
    if m.get("src"):
        data += f' data-src="{esc(m["src"])}"'
    if metrics:                                    # one readable chip: "$0.011 · 900ms"
        mp = []
        if "cost" in metrics:
            mp.append(f'${metrics["cost"]}')
        if "latency_ms" in metrics:
            mp.append(f'{metrics["latency_ms"]}ms')
        mp += [f"{k}={v}" for k, v in metrics.items() if k not in ("cost", "latency_ms")]
        data += f' data-metrics="{esc(" · ".join(mp))}"'
    head = f'<g class="{" ".join(cls)}" style="{";".join(style)}"{data}>'
    title = f'<title>{esc(m["text"])}</title>'      # native hover-reveal of the full label

    if m["type"] == "note":          # collapsed: a folded-page icon + a short tag; full text on click
        y, gx = m["y"], m["gx"]
        icon = _note_icon(gx + T.NOTE_ICON_W / 2, y)
        txt = _txt(gx + T.NOTE_ICON_W + 4, y, m["label"], T.FS_NOTE, T.INK_SOFT,
                   anchor="start", cls="mtx mcap")
        return head + title + icon + txt + "</g>"

    if m["type"] == "self":          # loop leaves + returns to the bar EDGE; text on the roomy side
        x, y = m["x"], m["y"]
        if m["side"] == "r":
            ex = x + T.BAR_HALF
            loop = f'<path class="arrow self" d="M{ex},{y} h20 v14 h-20" fill="none" stroke="{T.INK}" stroke-width="1.4"/>'
            ah, anchor = _arrowhead(ex, y + 14, False, T.INK, filled=True), "start"
        else:
            ex = x - T.BAR_HALF
            loop = f'<path class="arrow self" d="M{ex},{y} h-20 v14 h20" fill="none" stroke="{T.INK}" stroke-width="1.4"/>'
            ah, anchor = _arrowhead(ex, y + 14, True, T.INK, filled=True), "end"
        cap = m.get("caption", "")
        py = y + 2 if cap else y + 7                   # one-line primary + optional soft caption
        txt = _txt(m["lx"], py, m["lines"][0], T.FS_MSG, T.INK, anchor=anchor, cls="mtx")
        if cap:
            txt += _txt(m["lx"], py + 12, cap, T.FS_CAP, T.INK_SOFT, anchor=anchor, cls="mtx mcap")
        return head + title + loop + ah + txt + "</g>"

    # normal message — line spans bar-edge to bar-edge (set in layout). UML mechanics:
    # filled head = sync call · dashed + open head = return · solid + open head = async.
    # Label = a bold primary line ABOVE + an optional soft caption BELOW; centre clamped on-screen.
    # A drawn type-marker (api/io) sits just left of the primary.
    x0, x1, y = m["sx"], m["tx"], m["y"]
    ret = m["kind"] == "ret"
    openhead = ret or m["kind"] == "async"
    dash = ' stroke-dasharray="5 4"' if ret else ""
    line = (f'<line class="arrow {"ret" if ret else "sync"}" x1="{x0:.1f}" y1="{y}" '
            f'x2="{x1:.1f}" y2="{y}" stroke="{T.INK}" stroke-width="1.4"{dash} '
            f'style="--len:{abs(x1 - x0):.1f}"/>')
    ah = _arrowhead(x1, y, m["right"], T.INK, filled=not openhead)
    lcx = m["lcx"]
    txt = _txt(lcx, y - 8, m["lines"][0], T.FS_MSG, T.INK, cls="mtx")
    cap = m.get("caption", "")
    if cap:
        txt += _txt(lcx, y + 8, cap, T.FS_CAP, T.INK_SOFT, cls="mtx mcap")
    mk = _marker(m["marker"], lcx - m["pw"] / 2 - T.MARKER_PAD, y - 8) if m.get("marker") else ""
    return head + title + line + ah + mk + txt + "</g>"


def _slug(s):
    return "".join(ch if ch.isalnum() else "-" for ch in str(s).lower()).strip("-")


# ── lens / metric prep ─────────────────────────────────────────────────────────
def _prep_lenses(scn):
    """Compute per-message metric colours + the set of available lenses for a scenario."""
    msgs = scn.get("messages", [])
    cost_vals = [m["metrics"]["cost"] for m in msgs if "cost" in m.get("metrics", {})]
    lat_vals = [m["metrics"]["latency_ms"] for m in msgs if "latency_ms" in m.get("metrics", {})]
    def ramp(vals, v):
        lo, hi = (min(vals), max(vals)) if vals else (0, 1)
        t = 0.5 if hi == lo else (v - lo) / (hi - lo)     # all-equal → neutral amber
        return T.metric_color(t)                          # green(low) → red(high) heatmap
    for m in msgs:
        mm = m.get("metrics", {})
        if "cost" in mm:
            m["_ccost"] = ramp(cost_vals, mm["cost"])
        if "latency_ms" in mm:
            m["_clat"] = ramp(lat_vals, mm["latency_ms"])
    paths = []
    for m in msgs:
        for pa in m.get("paths", []):
            if pa not in paths:
                paths.append(pa)
    return {
        "paths": paths,
        "cost": (min(cost_vals), max(cost_vals)) if cost_vals else None,
        "latency_ms": (min(lat_vals), max(lat_vals)) if lat_vals else None,
    }


# ── card + page ────────────────────────────────────────────────────────────────
def emit_card(scn, n, active=False):
    sid = _slug(scn.get("id", f"s{n}"))
    lenses = _prep_lenses(scn)
    g = L.compute(scn)
    header, body, fill = emit_header(g, sid), emit_body(g, sid), _fill_bg(g)

    # lens toolbar (only lenses that have data)
    btns = ['<button class="lens on" data-lens="none">Neutral</button>']
    for pa in lenses["paths"]:
        btns.append(f'<button class="lens" data-lens="path-{_slug(pa)}">↪ {esc(pa)}</button>')
    if lenses["cost"]:
        lo, hi = lenses["cost"]
        btns.append('<button class="lens" data-lens="cost">$ cost</button>')
    if lenses["latency_ms"]:
        btns.append('<button class="lens" data-lens="lat">⏱ latency</button>')

    mk_api = f'<svg width="14" height="11" style="vertical-align:-2px">{_marker("api", 7, 5.5)}</svg>'
    mk_io = f'<svg width="14" height="11" style="vertical-align:-2px">{_marker("io", 7, 5.5)}</svg>'
    legends = [f'<div class="legend lg-none">solid&nbsp;→&nbsp;call &nbsp;·&nbsp; '
               f'dashed&nbsp;→&nbsp;return &nbsp;·&nbsp; open&nbsp;tip&nbsp;→&nbsp;async &nbsp;·&nbsp; '
               f'{mk_api}&nbsp;other&nbsp;service &nbsp;·&nbsp; {mk_io}&nbsp;data&nbsp;store &nbsp;·&nbsp; '
               f'▭&nbsp;active &nbsp;·&nbsp; click&nbsp;a&nbsp;row&nbsp;for&nbsp;detail</div>']
    for pa in lenses["paths"]:
        legends.append(f'<div class="legend lg-path-{_slug(pa)}" hidden>'
                       f'<span class="sw" style="background:{T.ACCENT}"></span> path “{esc(pa)}” lit; rest dimmed</div>')
    if lenses["cost"]:
        lo, hi = lenses["cost"]
        legends.append(f'<div class="legend lg-cost" hidden>cost '
                       f'<span class="ramp"></span> ${lo:.3f}–${hi:.3f} (low→high)</div>')
    if lenses["latency_ms"]:
        lo, hi = lenses["latency_ms"]
        legends.append(f'<div class="legend lg-lat" hidden>latency '
                       f'<span class="ramp"></span> {lo:.0f}–{hi:.0f} ms</div>')

    upd = (scn.get("meta", {}) or {}).get("updated", "")
    return f'''<section class="card{" active" if active else ""}" data-card="{sid}" data-title="{esc(scn.get("title",""))}" data-sub="{esc(scn.get("subtitle",""))}" data-updated="{esc(upd)}">
  <div class="head">{header}</div>
  <div class="scroll" style="{fill}"><div class="diagram lens-none">{body}</div></div>
  <div class="toolbar">
    <div class="lenses">{"".join(btns)}</div>
    <div class="tb-right"><div class="legends">{"".join(legends)}</div><button class="png">⤓ PNG</button></div>
  </div>
</section>'''


def emit_page(master):
    scns = master.get("scenarios") or [master]
    project = master.get("project", "") or "Diagrams"
    menu, cards = [], []
    for i, s in enumerate(scns):
        sid = _slug(s.get("id", f"s{i}"))
        menu.append(
            f'<button class="mitem{" active" if i == 0 else ""}" data-target="{sid}">'
            f'<span class="mi-title">{esc(s.get("title",""))}</span>'
            f'<span class="mi-sub">{esc(s.get("subtitle",""))}</span></button>')
        cards.append(emit_card(s, i, active=(i == 0)))
    solo = len(scns) == 1
    return (PAGE.replace("{{APPCLASS}}", "app solo" if solo else "app")
                .replace("{{PROJECT}}", esc(project))
                .replace("{{MENU}}", "" if solo else "".join(menu))
                .replace("{{CARDS}}", "\n".join(cards))
                .replace("{{CSS}}", CSS).replace("{{JS}}", JS)
                .replace("{{ACCENT}}", T.ACCENT).replace("{{PAPER}}", T.PAPER))


# ── CLI ─────────────────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        sys.exit("usage: render_html.py <spec.json> [out.html]")
    spec = json.load(open(sys.argv[1]))
    out = sys.argv[2] if len(sys.argv) > 2 else "index.html"
    open(out, "w").write(emit_page(spec))
    print(f"wrote {out}")


# ── frozen CSS / JS / PAGE shell (kept here so output is one self-contained file) ─
CSS = open(os.path.join(os.path.dirname(__file__), "assets", "app.css")).read() \
    if os.path.exists(os.path.join(os.path.dirname(__file__), "assets", "app.css")) else ""
JS = open(os.path.join(os.path.dirname(__file__), "assets", "app.js")).read() \
    if os.path.exists(os.path.join(os.path.dirname(__file__), "assets", "app.js")) else ""
PAGE = open(os.path.join(os.path.dirname(__file__), "assets", "page.html")).read() \
    if os.path.exists(os.path.join(os.path.dirname(__file__), "assets", "page.html")) else ""

if __name__ == "__main__":
    main()
