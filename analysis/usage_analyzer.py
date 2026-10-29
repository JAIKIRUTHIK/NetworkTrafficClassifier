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

            total_bytes_value = int(flow["total_bytes"])
            total_bytes += total_bytes_value

            category = flow["category"]
            protocol = flow["protocol"]
            destination = flow["destination_ip"]
            destination_port = flow["destination_port"]

            if category not in category_stats:
                category_stats[category] = {
                    "flows": 0,
                    "bytes": 0
                }

            category_stats[category]["flows"] += 1
            category_stats[category]["bytes"] += total_bytes_value

            if protocol not in protocol_stats:
                protocol_stats[protocol] = {
                    "flows": 0,
                    "bytes": 0
                }

            protocol_stats[protocol]["flows"] += 1
            protocol_stats[protocol]["bytes"] += total_bytes_value

            if destination not in destination_stats:
                destination_stats[destination] = {
                    "flows": 0,
                    "bytes": 0
                }

            destination_stats[destination]["flows"] += 1
            destination_stats[destination]["bytes"] += total_bytes_value

            if destination_port not in port_stats:
                port_stats[destination_port] = {
                    "flows": 0,
                    "bytes": 0
                }

            port_stats[destination_port]["flows"] += 1
            port_stats[destination_port]["bytes"] += total_bytes_value

    summary = []

    summary.append({
        "metric": "TOTAL",
        "name": "ALL",
        "flows": total_flows,
        "bytes": total_bytes
    })

    for category, values in category_stats.items():

        summary.append({
            "metric": "CATEGORY",
            "name": category,
            "flows": values["flows"],
            "bytes": values["bytes"]
        })

    for protocol, values in protocol_stats.items():

        summary.append({
            "metric": "PROTOCOL",
            "name": protocol,
            "flows": values["flows"],
            "bytes": values["bytes"]
        })

    for destination, values in destination_stats.items():

        summary.append({
            "metric": "DESTINATION",
            "name": destination,
            "flows": values["flows"],
            "bytes": values["bytes"]
        })

    for port, values in port_stats.items():

        summary.append({
            "metric": "PORT",
            "name": port,
            "flows": values["flows"],
            "bytes": values["bytes"]
        })

    return summary


def save_summary(summary):

    with open(SUMMARY_FILE, "w", newline="") as file:

        fieldnames = [
            "metric",
            "name",
            "flows",
            "bytes"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(summary)


def main():

    summary = analyze_usage()

    save_summary(summary)

    print("Usage analysis completed.")
    print("Summary records:", len(summary))
    print("Summary file:", SUMMARY_FILE)


if __name__ == "__main__":
    main()