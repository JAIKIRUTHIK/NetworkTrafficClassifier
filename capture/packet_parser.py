
from scapy.layers.inet import IP, TCP, UDP


def parse_packet(packet):
    """
    Convert an IPv4 packet into a structured dictionary.

    Returns:
        Dictionary containing packet information.
        Returns None for non-IPv4 packets.
    """

    # Ignore non-IPv4 packets
    if IP not in packet:
        return None

    record = {
        "timestamp": packet.time,
        "source_ip": packet[IP].src,
        "destination_ip": packet[IP].dst,
        "protocol": None,
        "source_port": None,
        "destination_port": None,
        "packet_size": len(packet)
    }

    # TCP packet
    if TCP in packet:
        record["protocol"] = "TCP"
        record["source_port"] = packet[TCP].sport
        record["destination_port"] = packet[TCP].dport

    # UDP packet
    elif UDP in packet:
        record["protocol"] = "UDP"
        record["source_port"] = packet[UDP].sport
        record["destination_port"] = packet[UDP].dport

    # Other IPv4 protocol
    else:
        record["protocol"] = str(packet[IP].proto)

    return record