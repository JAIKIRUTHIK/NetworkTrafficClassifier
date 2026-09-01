import streamlit as st
import pandas as pd


FILE = "data/device_usage.csv"


st.set_page_config(
    page_title="Network Traffic Dashboard",
    page_icon="🌐",
    layout="wide"
)


st.title("🌐 Network Traffic Dashboard")
st.write("Network usage monitoring and analysis")


df = pd.read_csv(FILE)


total_devices = len(df)
total_flows = df["total_flows"].sum()
total_bytes = df["total_bytes"].sum()

top_device = df.loc[
    df["total_bytes"].idxmax(),
    "device_ip"
]


col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "Total Devices",
    total_devices
)

col2.metric(
    "Total Flows",
    total_flows
)

col3.metric(
    "Total Traffic",
    f"{total_bytes / 1024:.2f} KB"
)

col4.metric(
    "Top Device",
    top_device
)


st.divider()


col1, col2 = st.columns(2)


with col1:

    st.subheader("Traffic by Category")

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

        category_df = category_df.set_index("Category")

        st.bar_chart(category_df)


with col2:

    st.subheader("Protocol Distribution")

    protocol_data = {
        "TCP": 0,
        "UDP": 0
    }

    classified_file = "data/classified_flows.csv"

    classified_df = pd.read_csv(classified_file)

    for protocol in protocol_data:

        protocol_data[protocol] = classified_df[
            classified_df["protocol"].str.strip() == protocol
        ]["total_bytes"].sum()

    protocol_df = pd.DataFrame(
        list(protocol_data.items()),
        columns=["Protocol", "Bytes"]
    )

    protocol_df = protocol_df.set_index("Protocol")

    st.bar_chart(protocol_df)


st.divider()


st.subheader("Top Devices by Traffic")


device_chart = df[
    ["device_ip", "total_bytes"]
].copy()


device_chart = device_chart.sort_values(
    "total_bytes",
    ascending=False
)


device_chart = device_chart.head(10)

device_chart = device_chart.set_index("device_ip")


st.bar_chart(device_chart)


st.divider()


st.subheader("Device Details")


device_list = sorted(
    df["device_ip"].unique()
)


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
    f"{device['total_bytes'] / 1024:.2f} KB"
)

col3.metric(
    "Device IP",
    selected_device
)


st.subheader("Traffic Categories for Selected Device")


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

    device_category_df = device_category_df.set_index(
        "Category"
    )

    st.bar_chart(device_category_df)

else:

    st.info("No categorized traffic found for this device.")


st.divider()


st.subheader("All Device Usage")

st.dataframe(
    df,
    use_container_width=True
)