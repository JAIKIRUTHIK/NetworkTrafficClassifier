import unittest

from features.feature_extractor import extract_features


class TestFeatureExtraction(unittest.TestCase):

    def test_feature_calculation(self):
        features = extract_features()

        self.assertGreater(len(features), 0)

        for feature in features:
            packet_count = int(feature["packet_count"])
            total_bytes = int(feature["total_bytes"])
            duration = float(feature["duration"])

            if duration > 0:
                expected_pps = packet_count / duration
                expected_bps = total_bytes / duration

                self.assertAlmostEqual(
                    float(feature["packets_per_second"]),
                    expected_pps,
                    places=10
                )

                self.assertAlmostEqual(
                    float(feature["bytes_per_second"]),
                    expected_bps,
                    places=10
                )

            else:
                self.assertEqual(
                    float(feature["packets_per_second"]),
                    0
                )

                self.assertEqual(
                    float(feature["bytes_per_second"]),
                    0
                )

    def test_feature_count(self):
        features = extract_features()

        self.assertGreater(len(features), 0)


if __name__ == "__main__":
    unittest.main()