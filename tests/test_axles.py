import unittest

from axles import calculate_tractor_axles, calculate_trailer_loads
from packing import PlacedPallet
from truck import CURTAINSIDER, FRIGO


class TruckGeometryTests(unittest.TestCase):

    def test_confirmed_trailer_profiles(self):
        self.assertEqual(CURTAINSIDER.trailer_length, 13.55)
        self.assertEqual(CURTAINSIDER.trailer_height, 2.68)
        self.assertEqual(CURTAINSIDER.external_trailer_length, 13.62)
        self.assertEqual(CURTAINSIDER.trailer_front_offset, 1.60)
        self.assertEqual(CURTAINSIDER.bogie_position, 7.70)
        self.assertAlmostEqual(CURTAINSIDER.kingpin_to_rear_bulkhead, 11.95)

        self.assertEqual(FRIGO.trailer_length, 13.31)
        self.assertEqual(FRIGO.trailer_height, 2.45)
        self.assertEqual(FRIGO.external_trailer_length, 13.68)
        self.assertEqual(FRIGO.trailer_front_offset, 1.68)
        self.assertEqual(FRIGO.bogie_position, 7.70)
        self.assertEqual(FRIGO.kingpin_to_rear_bulkhead, 11.63)

    def test_kingpin_load_uses_one_sixth_to_steer(self):
        steer, drive = calculate_tractor_axles(CURTAINSIDER, 6000)

        self.assertEqual(steer, 1000)
        self.assertEqual(drive, 5000)

    def test_trailer_beam_uses_the_truck_profile_geometry(self):
        # A 1,000 kg pallet whose centre sits 5.02 m behind the Frigo kingpin.
        pallet = PlacedPallet(
            description="Test",
            length=1.0,
            width=1.0,
            height=1.0,
            weight=1000,
            x=0.0,
            y=FRIGO.trailer_front_offset + FRIGO.uniform_payload_cg - 0.5,
        )

        kingpin, bogie, _ = calculate_trailer_loads(FRIGO, [pallet])

        self.assertAlmostEqual(bogie, 1000 * 5.02 / 7.70)
        self.assertAlmostEqual(kingpin + bogie, 1000)

    def test_rear_of_bogie_load_reduces_the_kingpin_reaction(self):
        # A pallet whose centre is 9 m behind the kingpin is rear of the
        # 7.70 m bogie centre.  It must unload the kingpin rather than have
        # its lever effect capped.
        pallet = PlacedPallet(
            description="Rear test",
            length=1.0,
            width=1.0,
            height=1.0,
            weight=1000,
            x=0.0,
            y=FRIGO.trailer_front_offset + 9.0 - 0.5,
        )

        kingpin, bogie, _ = calculate_trailer_loads(FRIGO, [pallet])

        self.assertLess(kingpin, 0)
        self.assertGreater(bogie, 1000)
        self.assertAlmostEqual(kingpin, 1000 * (7.70 - 9.0) / 7.70)
        self.assertAlmostEqual(kingpin + bogie, 1000)


if __name__ == "__main__":
    unittest.main()
