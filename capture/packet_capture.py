from scapy.all import sniff
from packet_parser import parse_packet
import csv
import os


CSV_FILE = "data/packets.csv"


def save_records(records):
    os.makedirs("data", exist_ok=True)

    fieldnames = [
        "timestamp",
        "source_ip",
        "destination_ip",
        "protocol",
        "source_port",
        "destination_port",
        "packet_size"
    ]

    with open(CSV_FILE, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


print("Starting packet capture...")
print("Capturing packets for 10 seconds...")
print()

packets = sniff(timeout=10)

records = []

for packet in packets:
    record = parse_packet(packet)

    if record is not None:
        records.append(record)

save_records(records)

print()
print("Packet capture completed.")
print("Total packets captured:", len(packets))
print("IPv4 records saved:", len(records))
print("CSV file:", CSV_FILE)