import unittest

import pandas as pd


class TestPipelineData(unittest.TestCase):

    def test_packet_flow_reconciliation(self):
        packets = pd.read_csv("data/packets.csv")
        flows = pd.read_csv("data/flows.csv")

        self.assertEqual(
            len(packets),
            int(flows["packet_count"].sum())
        )

        self.assertEqual(
            int(packets["packet_size"].sum()),
            int(flows["total_bytes"].sum())
        )

    def test_flow_feature_reconciliation(self):
        flows = pd.read_csv("data/flows.csv")
        features = pd.read_csv("data/flow_features.csv")

        self.assertEqual(len(flows), len(features))

        self.assertEqual(
            set(flows["flow_id"]),
            set(features["flow_id"])
        )

    def test_feature_classification_reconciliation(self):
        features = pd.read_csv("data/flow_features.csv")
        classified = pd.read_csv("data/classified_flows.csv")

        self.assertEqual(len(features), len(classified))

        self.assertEqual(
            set(features["flow_id"]),
            set(classified["flow_id"])
        )

        self.assertTrue(
            classified["category"].notna().all()
        )

        self.assertTrue(
            (classified["category"].str.strip() != "").all()
        )

    def test_device_reconciliation(self):
        classified = pd.read_csv("data/classified_flows.csv")
        devices = pd.read_csv("data/device_usage.csv")

        self.assertEqual(
            len(classified),
            int(devices["total_flows"].sum())
        )

        self.assertEqual(
            int(classified["total_bytes"].sum()),
            int(devices["total_bytes"].sum())
        )


if __name__ == "__main__":
    unittest.main()