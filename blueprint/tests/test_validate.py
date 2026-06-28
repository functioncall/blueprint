"""Unit tests for validate_master — the schema guardrail."""
import os
import sys
import json
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import validate_master as V  # noqa: E402

EX = os.path.join(os.path.dirname(__file__), "..", "examples")


def spec(**over):
    base = {
        "title": "t",
        "actors": [{"id": "a", "label": "A", "zone": "user"},
                   {"id": "b", "label": "B", "zone": "server"}],
        "messages": [{"from": "a", "to": "b", "text": "call"}],
    }
    base.update(over)
    return base


def load(name):
    with open(os.path.join(EX, name)) as f:
        return json.load(f)


class TestExamplesValidate(unittest.TestCase):
    def test_shipped_examples_have_no_errors(self):
        for f in ("web-request.json", "capture.json", "master-backdrop.json"):
            errs, _ = V.validate(load(f))
            self.assertEqual(errs, [], f"{f} should validate clean, got: {errs}")


class TestValidationRules(unittest.TestCase):
    def test_minimal_spec_ok(self):
        errs, _ = V.validate(spec())
        self.assertEqual(errs, [])

    def test_unknown_actor_ref(self):
        errs, _ = V.validate(spec(messages=[{"from": "a", "to": "zzz", "text": "x"}]))
        self.assertTrue(any("unknown actor" in e for e in errs), errs)

    def test_fragment_range_out_of_bounds(self):
        errs, _ = V.validate(spec(fragments=[{"kind": "opt", "range": [0, 9]}]))
        self.assertTrue(any("out of bounds" in e for e in errs), errs)

    def test_detail_must_be_object(self):
        errs, _ = V.validate(spec(messages=[{"from": "a", "to": "b", "text": "x", "detail": "nope"}]))
        self.assertTrue(any("detail" in e for e in errs), errs)

    def test_bad_via_rejected(self):
        errs, _ = V.validate(spec(messages=[{"from": "a", "to": "b", "text": "x", "via": "bogus"}]))
        self.assertTrue(any("via" in e for e in errs), errs)


if __name__ == "__main__":
    unittest.main()
