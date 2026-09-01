import csv

PACKET_FILE = "data/packets.csv"
FLOW_FILE = "data/flows.csv"


def create_flow_key(record):
    endpoint1 = (
        record["source_ip"],
        int(record["source_port"])
    )

    endpoint2 = (
        record["destination_ip"],
        int(record["destination_port"])
    )

    if endpoint1 <= endpoint2:
        return endpoint1, endpoint2, record["protocol"]

    return endpoint2, endpoint1, record["protocol"]


def build_flows():
    flows = {}

    with open(PACKET_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)

        for record in reader:

            if not record["source_ip"]:
                continue

            if not record["destination_ip"]:
                continue

            if not record["protocol"]:
                continue

            if not record["source_port"]:
                continue

            if not record["destination_port"]:
                continue

            key = create_flow_key(record)

            packet_size = int(record["packet_size"])
            timestamp = float(record["timestamp"])

            if key not in flows:
                flows[key] = {
                    "source_ip": record["source_ip"],
                    "destination_ip": record["destination_ip"],
                    "source_port": int(record["source_port"]),
                    "destination_port": int(record["destination_port"]),
                    "protocol": record["protocol"],
                    "packet_count": 0,
                    "start_time": timestamp,
                    "total_bytes": 0,
                    "end_time": timestamp
                }

            flow = flows[key]

            flow["packet_count"] += 1
            flow["total_bytes"] += packet_size

            if timestamp < flow["start_time"]:
                flow["start_time"] = timestamp

            if timestamp > flow["end_time"]:
                flow["end_time"] = timestamp

    return flows


def save_flows(flows):
    fieldnames = [
        "flow_id",
        "source_ip",
        "destination_ip",
        "source_port",
        "destination_port",
        "protocol",
        "packet_count",
        "total_bytes",
        "start_time",
        "end_time",
        "duration",
        "average_packet_size"
    ]

    with open(FLOW_FILE, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()

        flow_id = 1

        for flow in flows.values():

            duration = flow["end_time"] - flow["start_time"]

            average_packet_size = (
                flow["total_bytes"] / flow["packet_count"]
            )

            writer.writerow({
                "flow_id": flow_id,
                "source_ip": flow["source_ip"],
                "destination_ip": flow["destination_ip"],
                "source_port": flow["source_port"],
                "destination_port": flow["destination_port"],
                "protocol": flow["protocol"],
                "packet_count": flow["packet_count"],
                "total_bytes": flow["total_bytes"],
                "start_time": flow["start_time"],
                "end_time": flow["end_time"],
                "duration": round(duration, 6),
                "average_packet_size": round(average_packet_size, 2)
            })

            flow_id += 1


def main():
    flows = build_flows()

    save_flows(flows)

    print("Flow reconstruction completed.")
    print("Total flows:", len(flows))
    print("Flow file:", FLOW_FILE)


if __name__ == "__main__":
    main()