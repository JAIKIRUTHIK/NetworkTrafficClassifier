import csv

FLOW_FILE = "data/flows.csv"
FEATURE_FILE = "data/flow_features.csv"


def extract_features():
    features = []

    with open(FLOW_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)

        for flow in reader:
            packet_count = int(flow["packet_count"])
            total_bytes = int(flow["total_bytes"])
            duration = float(flow["duration"])

            if duration > 0:
                packets_per_second = packet_count / duration
                bytes_per_second = total_bytes / duration
            else:
                packets_per_second = 0
                bytes_per_second = 0

            record = {
                "flow_id": flow["flow_id"],
                "source_ip": flow["source_ip"],
                "destination_ip": flow["destination_ip"],
                "source_port": flow["source_port"],
                "destination_port": flow["destination_port"],
                "protocol": flow["protocol"],
                "packet_count": packet_count,
                "total_bytes": total_bytes,
                "duration": duration,
                "average_packet_size": float(flow["average_packet_size"]),
                "packets_per_second": round(packets_per_second, 2),
                "bytes_per_second": round(bytes_per_second, 2)
            }

            features.append(record)

    return features


def save_features(features):
    fieldnames = [
        "flow_id",
        "source_ip",
        "destination_ip",
        "source_port",
        "destination_port",
        "protocol",
        "packet_count",
        "total_bytes",
        "duration",
        "average_packet_size",
        "packets_per_second",
        "bytes_per_second"
    ]

    with open(FEATURE_FILE, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(features)


def main():
    features = extract_features()

    save_features(features)

    print("Feature extraction completed.")
    print("Total flows processed:", len(features))
    print("Feature file:", FEATURE_FILE)


if __name__ == "__main__":
    main()