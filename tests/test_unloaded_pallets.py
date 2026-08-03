import unittest

from cargo import CargoItem
from optimizer import optimize_load
from report import format_unloaded_pallets, generate_report
from truck import CURTAINSIDER


class UnloadedPalletTests(unittest.TestCase):

    def test_consecutive_unloaded_pallets_are_compressed_in_the_report(self):
        self.assertEqual(
            format_unloaded_pallets([("Apples", 3), ("Apples", 4), ("Apples", 5)]),
            "Apples #3-5",
        )

    def test_optimizer_identifies_the_unloaded_pallet(self):
        result = optimize_load(
            CURTAINSIDER,
            [CargoItem("Euro", 34, 1.20, 0.80, 1.60, 600)],
        )

        self.assertTrue(result.success)
        self.assertEqual(result.unloaded, [("Euro", 34)])
        self.assertIn("NOT LOADED: Euro #34", generate_report(CURTAINSIDER, result))


if __name__ == "__main__":
    unittest.main()
