import os
import pandas as pd


DEVICE_FILE = "data/device_usage.csv"
CLASSIFIED_FILE = "data/classified_flows.csv"
PACKET_FILE = "data/packets.csv"
FLOW_FILE = "data/flows.csv"
FEATURE_FILE = "data/flow_features.csv"
SUMMARY_FILE = "data/usage_summary.csv"


CATEGORY_COLUMNS = [
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


def format_bytes(value):

    value = float(value)

    if value < 1024:
        return f"{value:.0f} B"

    if value < 1024 * 1024:
        return f"{value / 1024:.2f} KB"

    if value < 1024 * 1024 * 1024:
        return f"{value / (1024 * 1024):.2f} MB"

    return f"{value / (1024 * 1024 * 1024):.2f} GB"


def file_exists(path):

    return os.path.exists(path)


def load_device_data():

    if not file_exists(DEVICE_FILE):
        return pd.DataFrame()

    return pd.read_csv(DEVICE_FILE)


def load_classified_data():

    if not file_exists(CLASSIFIED_FILE):
        return pd.DataFrame()

    return pd.read_csv(CLASSIFIED_FILE)


def load_packet_data():

    if not file_exists(PACKET_FILE):
        return pd.DataFrame()

    return pd.read_csv(PACKET_FILE)


def load_flow_data():

    if not file_exists(FLOW_FILE):
        return pd.DataFrame()

    return pd.read_csv(FLOW_FILE)


def load_feature_data():

    if not file_exists(FEATURE_FILE):
        return pd.DataFrame()

    return pd.read_csv(FEATURE_FILE)


def load_summary_data():

    if not file_exists(SUMMARY_FILE):
        return pd.DataFrame()

    return pd.read_csv(SUMMARY_FILE)


def get_network_statistics(device_df, classified_df):

    if device_df.empty:
        total_devices = 0
        total_flows = 0
        total_bytes = 0
    else:
        total_devices = len(device_df)
        total_flows = int(device_df["total_flows"].sum())
        total_bytes = int(device_df["total_bytes"].sum())

    if classified_df.empty:
        total_packets = 0
    else:
        total_packets = int(
            classified_df["packet_count"].sum()
        )

    return {
        "devices": total_devices,
        "flows": total_flows,
        "bytes": total_bytes,
        "packets": total_packets
    }


def get_category_data(device_df):

    if device_df.empty:
        return pd.DataFrame(
            columns=["Category", "Bytes"]
        )

    data = []

    for category in CATEGORY_COLUMNS:

        if category in device_df.columns:

            value = device_df[category].sum()

            if value > 0:

                data.append({
                    "Category": category,
                    "Bytes": value
                })

    result = pd.DataFrame(data)

    if not result.empty:

        result = result.sort_values(
            "Bytes",
            ascending=False
        )

    return result


def get_protocol_data(classified_df):

    if classified_df.empty:
        return pd.Series(dtype=float)

    data = classified_df.copy()

    data["protocol"] = (
        data["protocol"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    return (
        data
        .groupby("protocol")["total_bytes"]
        .sum()
        .sort_values(
            ascending=False
        )
    )


def get_top_devices(device_df, limit=10):

    if device_df.empty:
        return pd.DataFrame()

    return (
        device_df[
            ["device_ip", "total_bytes"]
        ]
        .sort_values(
            "total_bytes",
            ascending=False
        )
        .head(limit)
    )


def get_top_destinations(classified_df, limit=10):

    if classified_df.empty:
        return pd.Series(dtype=float)

    return (
        classified_df
        .groupby("destination_ip")["total_bytes"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(limit)
    )


def get_top_ports(classified_df, limit=10):

    if classified_df.empty:
        return pd.Series(dtype=float)

    return (
        classified_df
        .groupby("destination_port")["total_bytes"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(limit)
    )


def get_high_volume_flows(classified_df):

    if classified_df.empty:
        return pd.DataFrame()

    categories = [
        "High Volume HTTPS",
        "High Volume TCP",
        "High Volume UDP"
    ]

    return classified_df[
        classified_df["category"].isin(categories)
    ].copy()