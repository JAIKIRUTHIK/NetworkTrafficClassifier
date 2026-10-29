import unittest

from flow.flow_builder import create_flow_key


class TestFlowBuilder(unittest.TestCase):

    def test_bidirectional_flow_same_key(self):
        forward = {
            "source_ip": "192.168.1.10",
            "source_port": "50000",
            "destination_ip": "8.8.8.8",
            "destination_port": "443",
            "protocol": "TCP"
        }

        reverse = {
            "source_ip": "8.8.8.8",
            "source_port": "443",
            "destination_ip": "192.168.1.10",
            "destination_port": "50000",
            "protocol": "TCP"
        }

        self.assertEqual(
            create_flow_key(forward),
            create_flow_key(reverse)
        )

    def test_different_protocols_create_different_keys(self):
        tcp_flow = {
            "source_ip": "192.168.1.10",
            "source_port": "50000",
            "destination_ip": "8.8.8.8",
            "destination_port": "443",
            "protocol": "TCP"
        }

        udp_flow = {
            "source_ip": "192.168.1.10",
            "source_port": "50000",
            "destination_ip": "8.8.8.8",
            "destination_port": "443",
            "protocol": "UDP"
        }

        self.assertNotEqual(
            create_flow_key(tcp_flow),
            create_flow_key(udp_flow)
        )


if __name__ == "__main__":
    unittest.main()