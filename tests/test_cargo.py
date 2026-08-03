import unittest

from cargo import CargoItem
from truck import CURTAINSIDER


class CargoValidationTests(unittest.TestCase):

    def test_validation_rejects_cargo_over_the_trailer_height(self):
        item = CargoItem("Too tall cargo", 1, 1.20, 0.80, 3.00, 500)

        self.assertIn("Cargo dimensions exceed trailer", item.validate(CURTAINSIDER))


if __name__ == "__main__":
    unittest.main()
