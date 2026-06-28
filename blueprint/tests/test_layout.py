"""Unit tests for layout.compute — the pure geometry brain."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import layout as L  # noqa: E402


def scn(messages, actors=None):
    return {
        "actors": actors or [{"id": "a", "label": "A", "zone": "user"},
                             {"id": "b", "label": "B", "zone": "server"}],
        "messages": messages,
    }


class TestLayout(unittest.TestCase):
    def test_basic_compute(self):
        g = L.compute(scn([{"from": "a", "to": "b", "text": "call"},
                           {"from": "b", "to": "a", "text": "ret", "kind": "ret"}]))
        self.assertEqual(len(g["cols"]), 2)
        self.assertEqual(len(g["messages"]), 2)
        self.assertEqual(g["messages"][0]["route"], "A → B")

    def test_route_step_phase_present(self):
        g = L.compute(scn([{"from": "a", "to": "b", "text": "x"}]))
        m = g["messages"][0]
        for key in ("route", "step", "total", "phase"):
            self.assertIn(key, m)

    def test_from_equals_to_becomes_self(self):
        g = L.compute(scn([{"from": "a", "to": "a", "text": "loop"}]))
        self.assertEqual(g["messages"][0]["type"], "self")

    def test_unknown_ref_raises_valueerror(self):
        # must be ValueError (recoverable), NOT SystemExit (would kill the test runner)
        with self.assertRaises(ValueError):
            L.compute(scn([{"from": "a", "to": "zzz", "text": "x"}]))

    def test_step_numbering_skips_phases(self):
        g = L.compute(scn([{"phase": "P"},
                           {"from": "a", "to": "b", "text": "one"},
                           {"from": "a", "to": "b", "text": "two"}]))
        msgs = g["messages"]
        self.assertEqual((msgs[0]["step"], msgs[0]["total"]), (1, 2))
        self.assertEqual(msgs[1]["step"], 2)
        self.assertEqual(msgs[0]["phase"], "P")


if __name__ == "__main__":
    unittest.main()
