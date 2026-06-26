"""Pure geometry brain (DESIGN-v3 Phase 0/1). spec scenario -> positioned primitives.
No drawing, no I/O, no randomness -> deterministic + unit-testable. Ports the proven
x-layout + activation-bar req…ret stack + 2-line wrap from the v2 Pillow engine.

The emitter (render_html.py) turns this dict into SVG/HTML; it never recomputes geometry.
"""
import tokens as T


def _wrap(text, maxpx, fs, maxlines=2):
    """Word-wrap within maxpx to <=maxlines. Prefers splitting before a parenthetical
    (so '… (mic perm)' drops to its own line). Returns (lines, truncated)."""
    if T.text_w(text, fs) <= maxpx:
        return [text], False
    if " (" in text:                    # prefer the parenthetical as the break point
        i = text.index(" (")
        a, b = text[:i], text[i + 1:]
        if T.text_w(a, fs) <= maxpx and T.text_w(b, fs) <= maxpx:
            return [a, b], False
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if T.text_w(t, fs) <= maxpx or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    lines = [ln.strip(" ·") for ln in lines]       # no dangling separator at a wrap point
    truncated = len(lines) > maxlines
    lines = lines[:maxlines]
    if truncated:                       # ellipsize the last kept line to fit
        ln = lines[-1]
        while ln and T.text_w(ln + "…", fs) > maxpx:
            ln = ln[:-1]
        lines[-1] = ln.rstrip() + "…"
    return lines, truncated


_USERZ = {"user", "actor", "person", "customer"}
_CLIENTZ = {"client", "frontend", "mobile", "app", "device", "ui", "browser", "web"}
_SERVERZ = {"server", "backend", "api", "service", "gateway", "worker", "lambda", "function"}


def _neutral(a):
    """The human actor — kept a warm neutral so the coloured services pop."""
    return str(a.get("zone", "")).lower() in _USERZ


def _order_actors(actors, msgs):
    """Convention (not authoring order, not hard-coded): user → our client → our server →
    external third-party. Within a tier, busiest-first (more messages = further left), so the
    heavily-used external service sits near the server and rarely-used ones drift to the edge."""
    def tier(a):
        z = str(a.get("zone", "")).lower()
        if z in _USERZ: return 0
        if z in _CLIENTZ: return 1
        if z in _SERVERZ or a.get("kind") == "internal": return 2
        return 3                                    # external third-party
    key = {}
    for i, a in enumerate(actors):
        key[a.get("id", a["label"])] = i
        key[a["label"]] = i
    usage = [0] * len(actors)
    for m in msgs:
        refs = ([m["from"], m["to"]] if "from" in m else
                [m["self"]] if "self" in m else [m["note"]] if "note" in m else [])
        for i in {key.get(str(r).split(".")[0]) for r in refs}:
            if i is not None:
                usage[i] += 1
    return [actors[i] for i in sorted(range(len(actors)),
            key=lambda i: (tier(actors[i]), -usage[i], i))]


def compute(scenario):
    msgs = scenario.get("messages", [])
    actors = _order_actors(scenario.get("actors", []), msgs)

    # ── flatten actors -> columns; assign positional palette colours ──────────
    # color    = identity colour (drives the bar + the tier-2 sub label)
    # headcolor = the category base hue (drives the tier-1 actor label)
    n_hued = sum(0 if _neutral(a) else 1 for a in actors)
    cols, hi = [], 0
    for a in actors:
        aid = a.get("id", a["label"])
        subs = a.get("sub") or []
        if _neutral(a):
            base, slot = T.NEUTRAL, None
        else:
            base, slot = T.category_color(hi, n_hued), hi
            hi += 1
        if subs:
            k = len(subs)
            for j, s in enumerate(subs):
                col = T.NEUTRAL if slot is None else T.sub_color(slot, n_hued, j, k)
                cols.append({"actor": aid, "sub": s.get("id", s["label"]),
                             "key": f'{aid}.{s.get("id", s["label"])}',
                             "label": s["label"], "parent": a["label"],
                             "zone": a.get("zone"), "color": col, "headcolor": base,
                             "kind": a.get("kind", ""), "gfirst": j == 0,
                             "glast": j == len(subs) - 1, "subcap": ""})
        else:
            cols.append({"actor": aid, "sub": None, "key": aid, "label": a["label"],
                         "parent": None, "zone": a.get("zone"), "color": base, "headcolor": base,
                         "kind": a.get("kind", ""), "gfirst": True, "glast": True,
                         "subcap": a.get("sub_caption", a.get("kind", ""))})

    # name -> column index (actor.sub, bare actor -> first sub, label, id)
    name_to_i = {}
    for i, c in enumerate(cols):
        name_to_i[c["key"]] = i
        name_to_i.setdefault(c["actor"], i)
        name_to_i.setdefault(c["label"], i)
    def idx(ref):
        if ref in name_to_i:
            return name_to_i[ref]
        raise SystemExit(f"unknown actor '{ref}' — known: {sorted(set(name_to_i))}")

    # ── x positions: cells SPREAD to fill the canvas (colw widens to FILL_W) so the diagram
    #    is always full-bleed WITHOUT scaling fonts; contiguous groups, lifeline = cell centre ──
    colw = max(T.COLW, (T.FILL_W - T.RAIL_W) / max(1, len(cols)))
    x = float(T.RAIL_W)                   # reserve the left phase-index rail
    i = 0
    while i < len(cols):
        aid = cols[i]["actor"]
        grp = []
        while i < len(cols) and cols[i]["actor"] == aid:
            grp.append(cols[i]); i += 1
        for j, c in enumerate(grp):
            c["x"] = x + (j + 0.5) * colw
        x += len(grp) * colw
    width = x

    head_top = T.HEAD_TOP
    two_tier = any(c["sub"] for c in cols)
    has_cap = any(c["subcap"] for c in cols)
    hdr2 = two_tier or has_cap            # header needs a 2nd row for subs OR sub-captions
    head_h = T.TIER1_H + (T.TIER2_H if hdr2 else 0)
    head_region = head_top + head_h          # full header-SVG height; body lifelines start here
    life_top = head_region

    def cx(i):
        return cols[i]["x"]

    # ── header groups (one band per actor; lanes meet exactly -> no gaps) ──────
    order, seen = [], set()
    for c in cols:
        if c["actor"] not in seen:
            seen.add(c["actor"]); order.append(c["actor"])
    groups = []
    for aid in order:
        gc = [c for c in cols if c["actor"] == aid]
        groups.append({
            "parent": gc[0]["parent"] or gc[0]["label"], "lblcol": gc[0]["headcolor"],
            "kind": gc[0]["kind"], "subcap": gc[0]["subcap"],
            "x0": gc[0]["x"] - colw / 2, "x1": gc[-1]["x"] + colw / 2,
            "cx": (gc[0]["x"] + gc[-1]["x"]) / 2,
            "subs": [{"x": c["x"], "label": c["label"], "color": c["color"]} for c in gc] if len(gc) > 1 else [],
        })

    # ── message rows + phase gaps (cursor-based; phases add air, not a row) ────
    frag_starts = {fr["range"][0] for fr in scenario.get("fragments", [])}
    out_msgs, phases, y, ri = [], [], life_top + T.ROW_TOP, 0
    for m in msgs:
        if "phase" in m:
            y += T.PHASE_GAP
            phases.append({"y": y - T.PHASE_LEAD, "label": m.get("phase", "")})   # line sits a healthy gap above the next row
            continue
        if ri in frag_starts:                # room for the fragment's label tab
            y += T.FRAME_TOP
        ri += 1
        common = {"y": y, "kind": m.get("kind", ""), "paths": m.get("paths", []),
                  "metrics": m.get("metrics", {}), "src": m.get("src", ""),
                  "_ccost": m.get("_ccost"), "_clat": m.get("_clat")}
        if "note" in m:
            lines, _ = _wrap(m["text"], 176, T.FS_NOTE, 3)
            out_msgs.append({**common, "type": "note", "x": cx(idx(m["note"])),
                             "text": m["text"], "lines": lines})
        elif "self" in m:                  # text on whichever side has room (avoids sprawl)
            sci = idx(m["self"]); xx = cx(sci)
            loop_r = xx + T.BAR_HALF + 20
            right_room = width - 6 - (loop_r + 8)
            if right_room >= 92:
                lines, _ = _wrap(m["text"], min(right_room, 150), T.FS_MSG, 3)
                side, lx = "r", loop_r + 8
            else:
                left_room = (xx - T.BAR_HALF) - (T.RAIL_W + 6)
                lines, _ = _wrap(m["text"], max(80, min(left_room, 150)), T.FS_MSG, 3)
                side, lx = "l", xx - T.BAR_HALF - 8
            out_msgs.append({**common, "type": "self", "x": xx, "ci": sci, "text": m["text"],
                             "lines": lines, "side": side, "lx": lx})
        else:
            si, di = idx(m["from"]), idx(m["to"])
            sxx, txx = cx(si), cx(di)
            lines, _ = _wrap(m["text"], max(150, abs(txx - sxx) - 6), T.FS_MSG, 2)
            w = max(T.text_w(ln, T.FS_MSG) for ln in lines)
            lcx = min(max((sxx + txx) / 2, T.RAIL_W + 4 + w / 2), width - 6 - w / 2)  # clamp on-screen
            out_msgs.append({**common, "type": "msg", "si": si, "di": di,
                             "from_x": sxx, "to_x": txx, "mid_x": (sxx + txx) / 2, "lcx": lcx,
                             "right": txx >= sxx, "text": m["text"], "lines": lines})
        y += T.ROW
    life_bot = max((out_msgs[-1]["y"] if out_msgs else life_top) + 20, T.FILL_H)
    height = life_bot                        # extend to FILL_H so a short scenario fills the canvas

    # ── activation bars (req…ret stack; unreturned -> short bump) ─────────────
    bars, stack = [], {}
    for om in out_msgs:
        yy = om["y"]
        if om["type"] == "self":
            bars.append({"x": om["x"], "y0": yy - 4, "y1": yy + 18, "ci": om["ci"]})
        elif om["type"] == "note":
            continue
        elif om["kind"] == "ret" and stack.get(om["si"]):
            bars.append({"x": cx(om["si"]), "y0": stack[om["si"]].pop(), "y1": yy, "ci": om["si"]})
        else:
            stack.setdefault(om["di"], []).append(yy)
    for ci, ys in stack.items():
        for y0 in ys:
            bars.append({"x": cx(ci), "y0": y0, "y1": y0 + 18, "ci": ci})

    # ── arrow endpoints land on the OBJECT EDGE, never penetrating it ──────────
    def bar_at(xv, yv):
        return any(abs(b["x"] - xv) < 1 and b["y0"] - 0.6 <= yv <= b["y1"] + 0.6 for b in bars)
    for om in out_msgs:
        if om["type"] != "msg":
            continue
        yy, fx, tx, r = om["y"], om["from_x"], om["to_x"], om["right"]
        om["sx"] = (fx + T.BAR_HALF if r else fx - T.BAR_HALF) if bar_at(fx, yy) else fx
        om["tx"] = (tx - T.BAR_HALF if r else tx + T.BAR_HALF) if bar_at(tx, yy) else tx

    # ── combined fragments ─────────────────────────────────────────────────────
    frames = []
    for fr in scenario.get("fragments", []):
        a, b = fr["range"]
        rowset = out_msgs[a:b + 1]
        xsv = []
        for om in rowset:
            xsv += ([om["from_x"], om["to_x"]] if om["type"] == "msg" else [om["x"]])
        y1 = rowset[-1]["y"] + (24 if rowset[-1]["type"] == "self" else 13)  # clear self-call loop/bar
        frames.append({
            "kind": fr["kind"], "label": fr.get("label", ""),
            "guard0": (fr.get("segments") or [{}])[0].get("guard", ""),
            "x0": (min(xsv) if xsv else 0) - T.FRAME_PAD,
            "x1": (max(xsv) if xsv else width) + T.FRAME_PAD,
            "y0": rowset[0]["y"] - 32, "y1": y1,
            # a segment divider needs its own start index; the documented schema lets a
            # segment be just {guard}, so draw a divider only when a range is supplied.
            "divs": [{"y": out_msgs[s["range"][0]]["y"] - 15, "guard": s.get("guard", "")}
                     for s in fr.get("segments", [])[1:]
                     if isinstance(s.get("range"), list) and s.get("range")],
        })

    # phase bands for the left index rail (first spans from the top; last to the bottom)
    bands = [{"y0": life_top if k == 0 else ph["y"],
              "y1": phases[k + 1]["y"] if k + 1 < len(phases) else life_bot,
              "label": ph["label"]}
             for k, ph in enumerate(phases)]

    return {"width": round(width), "height": round(height),
            "head_region": head_region, "head_top": head_top, "head_h": head_h,
            "two_tier": two_tier, "hdr2": hdr2, "colw": colw, "life_top": life_top, "life_bot": life_bot,
            "cols": cols, "groups": groups, "bars": bars, "bands": bands,
            "messages": out_msgs, "frames": frames}
