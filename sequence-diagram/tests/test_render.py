"""Golden-snapshot + structural tests for the renderer.

The golden test is the guard for the skill's core promise: the SAME spec renders
byte-identical HTML every run. If you INTENTIONALLY change the renderer, tokens, or
assets, regenerate the goldens (run from the skill root):

    python3 tests/regen_golden.py

and review the diff before committing.
"""
import os
import sys
import json
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import render_html as R  # noqa: E402

EX = os.path.join(os.path.dirname(__file__), "..", "examples")
GOLD = os.path.join(os.path.dirname(__file__), "golden")
GOLDEN_SPECS = ("web-request", "capture")


def _read(path):
    with open(path) as f:
        return f.read()


class TestRenderGolden(unittest.TestCase):
    def _check(self, name):
        spec = json.loads(_read(os.path.join(EX, name + ".json")))
        got = R.emit_page(spec)
        want = _read(os.path.join(GOLD, name + ".html"))
        self.assertEqual(got, want,
                         f"{name}: rendered output drifted from golden — "
                         f"if intentional, run tests/regen_golden.py")

    def test_web_request_golden(self):
        self._check("web-request")

    def test_capture_golden(self):
        self._check("capture")


class TestRenderStructure(unittest.TestCase):
    def test_master_renders_one_card_per_scenario(self):
        m = json.loads(_read(os.path.join(EX, "master-backdrop.json")))
        html = R.emit_page(m)
        self.assertEqual(html.count('class="card'), len(m["scenarios"]))
        self.assertIn('id="switchMenu"', html)

    def test_bad_actor_ref_raises_valueerror(self):
        bad = {"actors": [{"id": "a", "label": "A", "zone": "user"}],
               "messages": [{"from": "a", "to": "ghost", "text": "x"}]}
        with self.assertRaises(ValueError):
            R.emit_page(bad)


if __name__ == "__main__":
    unittest.main()
