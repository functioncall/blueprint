#!/usr/bin/env python3
"""Regenerate the render golden snapshots. Run from the skill root after an
INTENTIONAL renderer/token/asset change, then review the diff before committing:

    python3 tests/regen_golden.py
"""
import os
import sys
import json

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import render_html as R  # noqa: E402

EX = os.path.join(HERE, "..", "examples")
GOLD = os.path.join(HERE, "golden")
SPECS = ("web-request", "capture")

os.makedirs(GOLD, exist_ok=True)
for name in SPECS:
    spec = json.load(open(os.path.join(EX, name + ".json")))
    out = os.path.join(GOLD, name + ".html")
    open(out, "w").write(R.emit_page(spec))
    print(f"wrote {out}")
