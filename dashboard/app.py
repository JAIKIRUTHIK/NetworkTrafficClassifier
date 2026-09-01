import streamlit as st
import pandas as pd


DEVICE_FILE = "data/device_usage.csv"
CLASSIFIED_FILE = "data/classified_flows.csv"


st.set_page_config(
    page_title="Network Traffic Dashboard",
    page_icon="🌐",
    layout="wide"
)


def format_bytes(value):

    if value < 1024:
        return f"{value:.0f} B"

    if value < 1024 * 1024:
        return f"{value / 1024:.2f} KB"

    if value < 1024 * 1024 * 1024:
        return f"{value / (1024 * 1024):.2f} MB"

    return f"{value / (1024 * 1024 * 1024):.2f} GB"


def load_data():

    device_df = pd.read_csv(DEVICE_FILE)
    classified_df = pd.read_csv(CLASSIFIED_FILE)

    return device_df, classified_df


st.title("🌐 Network Traffic Dashboard")

st.write(
    "Network usage monitoring, traffic classification "
    "and device-level analysis"
)


if st.button("🔄 Refresh Data"):

    st.cache_data.clear()

    st.rerun()


try:

    df, classified_df = load_data()

except Exception as error:

    st.error(f"Unable to load network data: {error}")

    st.stop()


total_devices = len(df)

total_flows = int(df["total_flows"].sum())

total_bytes = int(df["total_bytes"].sum())

total_packets = int(
    classified_df["packet_count"].sum()
)


if not df.empty:

    top_device_row = df.loc[
        df["total_bytes"].idxmax()
    ]

    top_device = top_device_row["device_ip"]

else:

    top_device = "N/A"


st.divider()


st.subheader("📊 Network Overview")


col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "Devices",
    total_devices
)


col2.metric(
    "Flows",
    total_flows
)


col3.metric(
    "Traffic",
    format_bytes(total_bytes)
)


col4.metric(
    "Packets",
    total_packets
)


st.divider()


st.subheader("📈 Traffic Analysis")


col1, col2 = st.columns(2)


category_columns = [
    "HTTPS/Web",
    "HTTP/Web",
    "DNS",
    "DHCP",
    "SSDP/UPnP",
    "Local Network Discovery",
    "Other TCP",
    "Other UDP"
]


with col1:

    st.write("### Traffic by Category")

    category_data = {}

    for category in category_columns:

        if category in df.columns:

            total = df[category].sum()

            if total > 0:

                category_data[category] = total


    category_df = pd.DataFrame(
        list(category_data.items()),
        columns=["Category", "Bytes"]
    )


    if not category_df.empty:

        category_df = category_df.sort_values(
            "Bytes",
            ascending=False
        )

        chart_df = category_df.set_index(
            "Category"
        )

        st.bar_chart(chart_df)

    else:

        st.info("No category data available.")


with col2:

    st.write("### Protocol Distribution")


    protocol_data = (
        classified_df
        .groupby("protocol")["total_bytes"]
        .sum()
        .sort_values(ascending=False)
    )


    if not protocol_data.empty:

        st.bar_chart(protocol_data)

    else:

        st.info("No protocol data available.")


st.divider()


st.subheader("🎯 Top Destination IPs")


destination_data = (
    classified_df
    .groupby("destination_ip")["total_bytes"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)


if not destination_data.empty:

    st.bar_chart(destination_data)

else:

    st.info("No destination data available.")


st.divider()


st.subheader("🔌 Top Destination Ports")


port_data = (
    classified_df
    .groupby("destination_port")["total_bytes"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)


if not port_data.empty:

    port_data.index = port_data.index.astype(str)

    st.bar_chart(port_data)

else:

    st.info("No port data available.")


st.divider()


st.subheader("💻 Top Devices by Traffic")


device_chart = df[
    ["device_ip", "total_bytes"]
].copy()


device_chart = device_chart.sort_values(
    "total_bytes",
    ascending=False
).head(10)


device_chart = device_chart.set_index(
    "device_ip"
)


st.bar_chart(device_chart)


st.divider()


st.subheader("🔍 Device Analysis")


device_list = sorted(
    df["device_ip"].unique()
)


if device_list:

    selected_device = st.selectbox(
        "Select a device",
        device_list
    )


    device = df[
        df["device_ip"] == selected_device
    ].iloc[0]


    col1, col2, col3 = st.columns(3)


    col1.metric(
        "Device Flows",
        int(device["total_flows"])
    )


    col2.metric(
        "Device Traffic",
        format_bytes(
            device["total_bytes"]
        )
    )


    col3.metric(
        "Device IP",
        selected_device
    )


    st.write(
        "### Traffic Categories"
    )


    device_categories = {}


    for category in category_columns:

        if category in df.columns:

            value = device[category]

            if value > 0:

                device_categories[category] = value


    if device_categories:

        device_category_df = pd.DataFrame(
            list(device_categories.items()),
            columns=["Category", "Bytes"]
        )


        device_category_df = (
            device_category_df
            .set_index("Category")
        )


        st.bar_chart(
            device_category_df
        )

    else:

        st.info(
            "No categorized traffic found."
        )


st.divider()


st.subheader("📋 All Device Usage")


st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)


st.divider()


st.caption(
    "Network Traffic Classifier and Usage Dashboard "
    "| Rule-based classification | No ML"
)