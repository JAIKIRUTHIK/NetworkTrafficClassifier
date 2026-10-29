import csv


INPUT_FILE = "data/classified_flows.csv"
OUTPUT_FILE = "data/device_usage.csv"


CATEGORIES = [
    "HTTPS/Web",
    "HTTP/Web",
    "DNS",
    "DHCP",
    "NTP",
    "QUIC",
    "High Volume HTTPS",
    "Streaming",
    "SSDP/UPnP",
    "Local Network Discovery",
    "High Volume TCP",
    "High Volume UDP",
    "Other TCP",
    "Other UDP",
    "Other"
]


def aggregate_devices():

    devices = {}

    with open(INPUT_FILE, "r", newline="") as file:

        reader = csv.DictReader(file)

        for flow in reader:

            source_ip = flow["source_ip"].strip()
            category = flow["category"].strip()

            total_bytes = int(flow["total_bytes"])

            if source_ip not in devices:

                devices[source_ip] = {
                    "device_ip": source_ip,
                    "total_flows": 0,
                    "total_bytes": 0
                }

                for category_name in CATEGORIES:
                    devices[source_ip][category_name] = 0

            devices[source_ip]["total_flows"] += 1
            devices[source_ip]["total_bytes"] += total_bytes

            if category in CATEGORIES:
                devices[source_ip][category] += total_bytes

    return devices


def save_devices(devices):

    fieldnames = [
        "device_ip",
        "total_flows",
        "total_bytes"
    ] + CATEGORIES

    with open(OUTPUT_FILE, "w", newline="") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for device in devices.values():
            writer.writerow(device)


def main():

    devices = aggregate_devices()

    save_devices(devices)

    print("Device aggregation completed.")
    print("Total devices:", len(devices))
    print("Output file:", OUTPUT_FILE)


if __name__ == "__main__":
    main()