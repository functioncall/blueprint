"""Unit tests for the design-token colour math (the frozen look's foundation)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import tokens as T  # noqa: E402

HEX = r"^#[0-9A-Fa-f]{6}$"


class TestMetricRamp(unittest.TestCase):
    def test_endpoints_are_ramp_stops(self):
        # low end == first stop (green), high end == last stop (red)
        self.assertEqual(T.metric_color(0).upper(), T.METRIC_RAMP[0].upper())
        self.assertEqual(T.metric_color(1).upper(), T.METRIC_RAMP[-1].upper())

    def test_clamps_out_of_range(self):
        self.assertEqual(T.metric_color(-5), T.metric_color(0))
        self.assertEqual(T.metric_color(9), T.metric_color(1))

    def test_always_valid_hex(self):
        for t in (0, 0.25, 0.5, 0.75, 1):
            self.assertRegex(T.metric_color(t), HEX)

    def test_low_is_green_high_is_red(self):
        lo, hi = T._hex(T.metric_color(0)), T._hex(T.metric_color(1))
        self.assertGreater(lo[1], lo[0])   # at low cost, green channel beats red
        self.assertGreater(hi[0], hi[1])   # at high cost, red channel beats green


class TestColourHelpers(unittest.TestCase):
    def test_oklch_hex_format(self):
        self.assertRegex(T.oklch_hex(0.6, 0.1, 200), HEX)

    def test_category_color_format(self):
        for i in range(5):
            self.assertRegex(T.category_color(i, 5), HEX)

    def test_darken_returns_hex(self):
        self.assertRegex(T.darken("#2FA05A"), HEX)


class TestTextWidth(unittest.TestCase):
    def test_deterministic_and_monotonic(self):
        self.assertEqual(T.text_w("abc", 10), T.text_w("abc", 10))
        self.assertGreater(T.text_w("abcdef", 10), T.text_w("abc", 10))


if __name__ == "__main__":
    unittest.main()
