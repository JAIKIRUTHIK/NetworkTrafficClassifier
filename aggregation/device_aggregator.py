import csv


INPUT_FILE = "data/classified_flows.csv"
OUTPUT_FILE = "data/device_usage.csv"


def aggregate_devices():

    devices = {}

    with open(INPUT_FILE, "r", newline="") as file:

        reader = csv.DictReader(file)

        for flow in reader:

            source_ip = flow["source_ip"]
            category = flow["category"]

            total_bytes = int(flow["total_bytes"])

            if source_ip not in devices:

                devices[source_ip] = {
                    "device_ip": source_ip,
                    "total_flows": 0,
                    "total_bytes": 0,
                    "HTTPS/Web": 0,
                    "HTTP/Web": 0,
                    "DNS": 0,
                    "DHCP": 0,
                    "SSDP/UPnP": 0,
                    "Local Network Discovery": 0,
                    "Other TCP": 0,
                    "Other UDP": 0
                }

            devices[source_ip]["total_flows"] += 1
            devices[source_ip]["total_bytes"] += total_bytes

            if category in devices[source_ip]:

                devices[source_ip][category] += total_bytes

    return devices


def save_devices(devices):

    fieldnames = [
        "device_ip",
        "total_flows",
        "total_bytes",
        "HTTPS/Web",
        "HTTP/Web",
        "DNS",
        "DHCP",
        "SSDP/UPnP",
        "Local Network Discovery",
        "Other TCP",
        "Other UDP"
    ]

    with open(OUTPUT_FILE, "w", newline="") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for device in devices.values():

            writer.writerow(device)


devices = aggregate_devices()

save_devices(devices)

print("Device aggregation completed.")
print("Total devices:", len(devices))
print("Output file:", OUTPUT_FILE)