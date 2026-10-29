import csv


FEATURE_FILE = "data/flow_features.csv"
CLASSIFIED_FILE = "data/classified_flows.csv"


STREAMING_PORTS = {
    554,
    1755,
    1935,
    5004,
    5005
}


def classify_flow(flow):

    protocol = flow["protocol"].strip().upper()

    source_port = int(flow["source_port"])
    destination_port = int(flow["destination_port"])

    destination_ip = flow["destination_ip"].strip()

    packet_count = int(flow["packet_count"])
    bytes_per_second = float(flow["bytes_per_second"])

    ports = {source_port, destination_port}


    if protocol in {"TCP", "UDP"} and 53 in ports:
        return "DNS"


    if protocol == "UDP" and ports.intersection({67, 68}):
        return "DHCP"


    if protocol == "UDP" and 123 in ports:
        return "NTP"


    if protocol == "UDP" and 1900 in ports:
        return "SSDP/UPnP"


    if protocol == "UDP" and 5353 in ports:
        return "Local Network Discovery"


    if protocol == "UDP" and ports.intersection({137, 138, 139}):
        return "Local Network Discovery"


    if protocol == "UDP" and 443 in ports:
        return "QUIC"


    if protocol in {"TCP", "UDP"} and ports.intersection(STREAMING_PORTS):
        return "Streaming"


    if protocol == "TCP" and 80 in ports:
        return "HTTP/Web"


    if protocol == "TCP" and 443 in ports:

        if packet_count >= 20 and bytes_per_second > 100000:
            return "High Volume HTTPS"

        return "HTTPS/Web"


    if protocol == "TCP":

        if packet_count >= 20 and bytes_per_second > 100000:
            return "High Volume TCP"

        return "Other TCP"


    if protocol == "UDP":

        if packet_count >= 20 and bytes_per_second > 50000:
            return "High Volume UDP"

        return "Other UDP"


    return "Other"


def classify_flows():

    classified = []

    with open(FEATURE_FILE, "r", newline="") as file:

        reader = csv.DictReader(file)

        for flow in reader:

            category = classify_flow(flow)

            flow["category"] = category

            classified.append(flow)

    return classified


def save_classified_flows(flows):

    if not flows:
        return

    fieldnames = list(flows[0].keys())

    with open(CLASSIFIED_FILE, "w", newline="") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(flows)


def main():

    classified = classify_flows()

    save_classified_flows(classified)

    print("Traffic classification completed.")
    print("Total flows classified:", len(classified))
    print("Classified file:", CLASSIFIED_FILE)


if __name__ == "__main__":
    main()