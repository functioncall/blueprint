#!/usr/bin/env python3
"""Validate a spec / master file against the v3 schema that render_html.py consumes.
Deterministic guardrail so discovery-agent output is verified before it's trusted.
Prints errors; exit 1 on any.

Schema (v3): actors live PER SCENARIO (not top-level). A message is one of:
  {from,to,text}  (+ "kind":"ret", "metrics":{}, "paths":[], "src", "detail":{})  request / return
  {self,text}                                                          self-loop
  {note,text}                                                          aside box
  {phase:"LABEL"}                                                      section divider (no text/refs)
Per scenario, optional "fragments":[{kind,label,range:[a,b],segments?}] where a,b index
the NON-phase message order. A bare single-diagram spec (top-level actors+messages, no
"scenarios") is also accepted.

Usage: python3 validate_master.py <spec_or_master.json>
"""
import json
import sys

KINDS = {"", "internal", "external"}
MKINDS = {"msg", "ret", "async"}          # call(default) · dashed return · solid open-head async
VIA = {"fn", "api", "io"}                 # fn(default,no marker) · api(boundary) · io(data store)
FRAG_KINDS = {"opt", "alt", "loop", "par", "break", "critical", "ref"}
DETAIL_KEYS = {"why", "sends", "effects", "fails", "ordering", "auth"}   # AI click-box body
BANNED = ("·", "—")             # middot · / em-dash — : clause-stuffing, not allowed in a PRIMARY label
PRIMARY_MAXCH, CAP_MAXCH, NOTE_MAXCH, DETAIL_MAXCH = 30, 36, 24, 160


def _validate_scenario(sc, sid, errs, warns):
    actors = sc.get("actors")
    if not isinstance(actors, list) or not actors:
        errs.append(f"scenario '{sid}': 'actors' must be a non-empty list")
        return

    ids = {}                      # actor id/label -> set of sub ids
    for a in actors:
        if not a.get("label"):
            errs.append(f"scenario '{sid}': an actor is missing 'label'")
            continue
        if a.get("kind", "") not in KINDS:
            errs.append(f"scenario '{sid}' actor '{a['label']}': kind must be one of {sorted(KINDS)}")
        subs = a.get("sub") or []
        if not isinstance(subs, list):
            errs.append(f"scenario '{sid}' actor '{a['label']}': 'sub' must be a list")
            subs = []
        sset = {s.get("id", s.get("label", "")) for s in subs}
        ids[a.get("id", a["label"])] = sset
        ids.setdefault(a["label"], sset)

    def ref_ok(ref):
        return str(ref).partition(".")[0] in ids   # bare sub tolerated

    msgs = sc.get("messages")
    if not isinstance(msgs, list) or not msgs:
        errs.append(f"scenario '{sid}': 'messages' must be a non-empty list")
        return
    nm = 0                        # count of NON-phase (rendered) messages, for fragment bounds
    for j, msg in enumerate(msgs):
        tag = f"scenario '{sid}' msg[{j}]"
        if "phase" in msg:
            if not str(msg.get("phase", "")).strip():
                errs.append(f"{tag}: empty 'phase' label")
            continue
        nm += 1
        is_arrow = False
        if "from" in msg and "to" in msg:
            is_arrow = True
            for r in (msg["from"], msg["to"]):
                if not ref_ok(r):
                    errs.append(f"{tag}: unknown actor '{r}'")
            if msg.get("kind", "msg") not in MKINDS:
                errs.append(f"{tag}: kind must be msg|ret|async")
            if msg.get("via") is not None and msg["via"] not in VIA:
                errs.append(f"{tag}: via must be one of {sorted(VIA)}")
            if msg["from"] == msg["to"]:
                warns.append(f"{tag}: from==to ('{msg['from']}') — use {{self: ...}} for a self-call")
        elif "self" in msg:
            is_arrow = True
            if not ref_ok(msg["self"]):
                errs.append(f"{tag}: unknown actor '{msg['self']}'")
        elif "note" in msg:
            if not ref_ok(msg["note"]):
                errs.append(f"{tag}: unknown actor '{msg['note']}'")
        else:
            errs.append(f"{tag}: must be from/to, self, note, or phase")
        if "note" not in msg and not msg.get("text"):
            errs.append(f"{tag}: missing 'text'")
        # label hygiene — primary arrow/self labels stay ONE short clause (detail → caption)
        text = msg.get("text", "") or ""
        if is_arrow:
            for ch in BANNED:
                if ch in text:
                    errs.append(f"{tag}: '{ch}' not allowed in a primary label "
                                f"(one clause only — move detail to 'caption'): {text!r}")
            if len(text) > PRIMARY_MAXCH:
                warns.append(f"{tag}: primary label {len(text)}>{PRIMARY_MAXCH} chars: {text!r}")
        elif "note" in msg:                 # notes are now a short tag (icon + label); detail → src
            for ch in BANNED:
                if ch in text:
                    errs.append(f"{tag}: '{ch}' not allowed in a note tag: {text!r}")
            if len(text) > NOTE_MAXCH:
                warns.append(f"{tag}: note tag {len(text)}>{NOTE_MAXCH} chars "
                             f"(keep it a short label; put detail in 'src'): {text!r}")
        cap = msg.get("caption")
        if cap is not None and len(cap) > CAP_MAXCH:
            warns.append(f"{tag}: caption {len(cap)}>{CAP_MAXCH} chars: {cap!r}")
        if msg.get("metrics") is not None and not isinstance(msg["metrics"], dict):
            errs.append(f"{tag}: 'metrics' must be an object")
        if msg.get("paths") is not None and not isinstance(msg["paths"], list):
            errs.append(f"{tag}: 'paths' must be a list")
        det = msg.get("detail")                 # AI-prefilled click-box body; every key optional
        if det is not None:
            if not isinstance(det, dict):
                errs.append(f"{tag}: 'detail' must be an object")
            else:
                for dk, dv in det.items():
                    if dk not in DETAIL_KEYS:
                        warns.append(f"{tag}: detail key '{dk}' unknown ({sorted(DETAIL_KEYS)})")
                    elif dv is not None and not isinstance(dv, str):
                        errs.append(f"{tag}: detail.{dk} must be a string")
                    elif isinstance(dv, str) and len(dv) > DETAIL_MAXCH:
                        warns.append(f"{tag}: detail.{dk} {len(dv)}>{DETAIL_MAXCH} chars "
                                     f"(keep each a tight clause): {dv!r}")

    for fr in sc.get("fragments", []) or []:
        if fr.get("kind") and fr["kind"] not in FRAG_KINDS:
            errs.append(f"scenario '{sid}': fragment kind '{fr['kind']}' unknown ({sorted(FRAG_KINDS)})")
        rng = fr.get("range")
        ok = (isinstance(rng, list) and len(rng) == 2
              and all(isinstance(x, int) for x in rng) and 0 <= rng[0] <= rng[1] < nm)
        if not ok:
            errs.append(f"scenario '{sid}': fragment range {rng} out of bounds "
                        f"(must be [a,b] with 0<=a<=b<{nm}, indexing non-phase messages)")
        elif rng[0] == rng[1] and fr.get("kind") != "loop":
            warns.append(f"scenario '{sid}': {fr.get('kind')} fragment wraps a single message "
                         f"{rng} — a box is for ≥2 messages; fold the condition into that "
                         f"message's caption instead (a 1-message loop is the only exception)")


def validate(m):
    if not isinstance(m, dict):
        return ["top level must be an object"], []
    errs, warns = [], []
    if not isinstance(m.get("provenance", {}), dict):
        errs.append("'provenance' must be an object")
    scns = m.get("scenarios")
    if scns is None and m.get("actors") and m.get("messages"):
        scns = [m]                                  # bare single-diagram spec
    if not isinstance(scns, list) or not scns:
        return errs + ["'scenarios' must be a non-empty list (or a bare spec with top-level actors+messages)"], warns
    seen = set()
    for i, sc in enumerate(scns):
        sid = sc.get("id", f"#{i}")
        if sid in seen:
            errs.append(f"duplicate scenario id '{sid}'")
        seen.add(sid)
        _validate_scenario(sc, sid, errs, warns)
    return errs, warns


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_master.py <spec_or_master.json>")
    try:
        m = json.load(open(sys.argv[1]))
    except json.JSONDecodeError as e:
        raise SystemExit(f"INVALID JSON: {e}")
    errs, warns = validate(m)
    for w in warns:
        print("  warn:", w)
    if errs:
        print("INVALID:")
        for e in errs:
            print("  -", e)
        sys.exit(1)
    scns = m.get("scenarios") or [m]
    print(f"OK — {len(scns)} scenario(s); "
          + ", ".join(f"{s.get('id', '#'+str(i))}:{len(s.get('actors', []))}a/"
                      f"{sum(1 for x in s.get('messages', []) if 'phase' not in x)}m"
                      for i, s in enumerate(scns)))


if __name__ == "__main__":
    main()
