import unittest

from classifier.rule_classifier import classify_flow


def make_flow(
    protocol="TCP",
    source_port=50000,
    destination_port=50001,
    packet_count=1,
    bytes_per_second=0,
    destination_ip="8.8.8.8"
):
    return {
        "protocol": protocol,
        "source_port": source_port,
        "destination_port": destination_port,
        "packet_count": packet_count,
        "bytes_per_second": bytes_per_second,
        "destination_ip": destination_ip
    }


class TestClassifier(unittest.TestCase):

    def test_dns(self):
        flow = make_flow(protocol="UDP", destination_port=53)
        self.assertEqual(classify_flow(flow), "DNS")

    def test_dhcp(self):
        flow = make_flow(protocol="UDP", source_port=68, destination_port=67)
        self.assertEqual(classify_flow(flow), "DHCP")

    def test_ntp(self):
        flow = make_flow(protocol="UDP", destination_port=123)
        self.assertEqual(classify_flow(flow), "NTP")

    def test_ssdp(self):
        flow = make_flow(
            protocol="UDP",
            destination_port=1900,
            destination_ip="239.255.255.250"
        )
        self.assertEqual(classify_flow(flow), "SSDP/UPnP")

    def test_mdns(self):
        flow = make_flow(
            protocol="UDP",
            source_port=5353,
            destination_port=5353,
            destination_ip="224.0.0.251"
        )
        self.assertEqual(classify_flow(flow), "Local Network Discovery")

    def test_netbios_discovery(self):
        flow = make_flow(protocol="UDP", destination_port=137)
        self.assertEqual(classify_flow(flow), "Local Network Discovery")

    def test_quic(self):
        flow = make_flow(protocol="UDP", destination_port=443)
        self.assertEqual(classify_flow(flow), "QUIC")

    def test_streaming(self):
        flow = make_flow(protocol="TCP", destination_port=554)
        self.assertEqual(classify_flow(flow), "Streaming")

    def test_http(self):
        flow = make_flow(protocol="TCP", destination_port=80)
        self.assertEqual(classify_flow(flow), "HTTP/Web")

    def test_https(self):
        flow = make_flow(protocol="TCP", destination_port=443)
        self.assertEqual(classify_flow(flow), "HTTPS/Web")

    def test_high_volume_https(self):
        flow = make_flow(
            protocol="TCP",
            destination_port=443,
            packet_count=20,
            bytes_per_second=100001
        )
        self.assertEqual(classify_flow(flow), "High Volume HTTPS")

    def test_other_tcp(self):
        flow = make_flow(protocol="TCP", destination_port=5000)
        self.assertEqual(classify_flow(flow), "Other TCP")

    def test_high_volume_tcp(self):
        flow = make_flow(
            protocol="TCP",
            destination_port=5000,
            packet_count=20,
            bytes_per_second=100001
        )
        self.assertEqual(classify_flow(flow), "High Volume TCP")

    def test_high_volume_udp(self):
        flow = make_flow(
            protocol="UDP",
            destination_port=5000,
            packet_count=20,
            bytes_per_second=50001
        )
        self.assertEqual(classify_flow(flow), "High Volume UDP")

    def test_other_udp(self):
        flow = make_flow(protocol="UDP", destination_port=5000)
        self.assertEqual(classify_flow(flow), "Other UDP")

    def test_other_protocol(self):
        flow = make_flow(protocol="1")
        self.assertEqual(classify_flow(flow), "Other")


if __name__ == "__main__":
    unittest.main()