import csv


FEATURE_FILE = "data/flow_features.csv"
CLASSIFIED_FILE = "data/classified_flows.csv"


def classify_flow(flow):

    protocol = flow["protocol"].strip().upper()

    source_port = int(flow["source_port"])
    destination_port = int(flow["destination_port"])

    source_ip = flow["source_ip"].strip()
    destination_ip = flow["destination_ip"].strip()

    packet_count = int(flow["packet_count"])
    total_bytes = int(flow["total_bytes"])
    duration = float(flow["duration"])
    average_packet_size = float(flow["average_packet_size"])
    packets_per_second = float(flow["packets_per_second"])
    bytes_per_second = float(flow["bytes_per_second"])

    ports = {source_port, destination_port}


    # DNS

    if protocol == "UDP" and 53 in ports:
        return "DNS"


    # DHCP

    if protocol == "UDP" and ports.intersection({67, 68}):
        return "DHCP"


    # SSDP / UPnP

    if protocol == "UDP" and 1900 in ports:
        return "SSDP/UPnP"


    # mDNS

    if protocol == "UDP" and 5353 in ports:
        return "Local Network Discovery"


    # NetBIOS

    if protocol == "UDP" and ports.intersection({137, 138}):
        return "Local Network Discovery"


    # QUIC

    if protocol == "UDP" and 443 in ports:
        return "QUIC"


    # HTTP

    if protocol == "TCP" and 80 in ports:
        return "HTTP/Web"


    # HTTPS

    if protocol == "TCP" and 443 in ports:

        if bytes_per_second > 500000 and average_packet_size > 800:
            return "High Volume HTTPS"

        return "HTTPS/Web"


    # Multicast / Broadcast traffic

    if protocol == "UDP":

        if (
            destination_ip.startswith("224.")
            or destination_ip.startswith("239.")
            or destination_ip == "255.255.255.255"
        ):

            return "Local Network Discovery"


    # High volume TCP

    if protocol == "TCP":

        if packet_count >= 20 and bytes_per_second > 100000:
            return "High Volume TCP"

        return "Other TCP"


    # High volume UDP

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

    print(
        "Total flows classified:",
        len(classified)
    )

    print(
        "Classified file:",
        CLASSIFIED_FILE
    )


if __name__ == "__main__":

    main()