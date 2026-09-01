import csv

CLASSIFIED_FILE = "data/classified_flows.csv"
SUMMARY_FILE = "data/usage_summary.csv"


def analyze_usage():
    total_flows = 0
    total_bytes = 0

    category_stats = {}
    protocol_stats = {}
    destination_stats = {}
    port_stats = {}

    with open(CLASSIFIED_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)

        for flow in reader:
            total_flows += 1

            bytes_used = int(flow["total_bytes"])
            total_bytes += bytes_used

            category = flow["category"].strip()
            protocol = flow["protocol"].strip().upper()
            destination = flow["destination_ip"].strip()
            destination_port = flow["destination_port"].strip()

            if category not in category_stats:
                category_stats[category] = {
                    "flows": 0,
                    "bytes": 0
                }

            category_stats[category]["flows"] += 1
            category_stats[category]["bytes"] += bytes_used

            if protocol not in protocol_stats:
                protocol_stats[protocol] = {
                    "flows": 0,
                    "bytes": 0
                }

            protocol_stats[protocol]["flows"] += 1
            protocol_stats[protocol]["bytes"] += bytes_used

            if destination not in destination_stats:
                destination_stats[destination] = 0

            destination_stats[destination] += bytes_used

            if destination_port not in port_stats:
                port_stats[destination_port] = 0

            port_stats[destination_port] += bytes_used

    return (
        total_flows,
        total_bytes,
        category_stats,
        protocol_stats,
        destination_stats,
        port_stats
    )


def save_summary(
    total_flows,
    total_bytes,
    category_stats,
    protocol_stats,
    destination_stats,
    port_stats
):
    with open(SUMMARY_FILE, "w", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            "Metric",
            "Name",
            "Flows",
            "Bytes"
        ])

        writer.writerow([
            "TOTAL",
            "All Traffic",
            total_flows,
            total_bytes
        ])

        for category, stats in category_stats.items():
            writer.writerow([
                "CATEGORY",
                category,
                stats["flows"],
                stats["bytes"]
            ])

        for protocol, stats in protocol_stats.items():
            writer.writerow([
                "PROTOCOL",
                protocol,
                stats["flows"],
                stats["bytes"]
            ])

        for destination, bytes_used in destination_stats.items():
            writer.writerow([
                "DESTINATION",
                destination,
                "",
                bytes_used
            ])

        for port, bytes_used in port_stats.items():
            writer.writerow([
                "PORT",
                port,
                "",
                bytes_used
            ])


def main():
    (
        total_flows,
        total_bytes,
        category_stats,
        protocol_stats,
        destination_stats,
        port_stats
    ) = analyze_usage()

    save_summary(
        total_flows,
        total_bytes,
        category_stats,
        protocol_stats,
        destination_stats,
        port_stats
    )

    print("Usage analysis completed.")
    print("Total flows:", total_flows)
    print("Total bytes:", total_bytes)
    print("Summary file:", SUMMARY_FILE)


if __name__ == "__main__":
    main()