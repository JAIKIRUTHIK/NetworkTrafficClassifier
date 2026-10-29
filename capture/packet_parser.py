
from scapy.layers.inet import IP, TCP, UDP


def parse_packet(packet):
    
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

    
    if TCP in packet:
        record["protocol"] = "TCP"
        record["source_port"] = packet[TCP].sport
        record["destination_port"] = packet[TCP].dport

    
    elif UDP in packet:
        record["protocol"] = "UDP"
        record["source_port"] = packet[UDP].sport
        record["destination_port"] = packet[UDP].dport

    
    else:
        record["protocol"] = str(packet[IP].proto)

    return record