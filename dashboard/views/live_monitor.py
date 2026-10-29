import ipaddress

import threading

from collections import deque


import streamlit as st

from scapy.all import AsyncSniffer, get_if_list


from capture.packet_parser import parse_packet

from classifier.rule_classifier import classify_flow


MAX_LIVE_PACKETS = 500

MAX_LIVE_FLOWS = 500

LIVE_REFRESH_INTERVAL = 1


live_packets = deque(
    maxlen=MAX_LIVE_PACKETS
)


live_flows = {}


live_lock = threading.Lock()


live_capture_count = 0

live_capture_bytes = 0


live_sniffer = None


def create_flow_key(record):

    protocol = record["protocol"]

    source_ip = record["source_ip"]

    destination_ip = record["destination_ip"]

    source_port = record["source_port"]

    destination_port = record["destination_port"]


    if source_port is None:

        source_port = 0


    if destination_port is None:

        destination_port = 0


    endpoint1 = (
        source_ip,
        int(source_port)
    )


    endpoint2 = (
        destination_ip,
        int(destination_port)
    )


    if endpoint1 <= endpoint2:

        return (
            endpoint1,
            endpoint2,
            protocol
        )


    return (
        endpoint2,
        endpoint1,
        protocol
    )


def is_local_device(ip_address):

    try:

        address = ipaddress.ip_address(
            ip_address
        )


        return address.is_private


    except ValueError:

        return False


def packet_callback(packet):

    global live_capture_count

    global live_capture_bytes


    record = parse_packet(packet)


    if record is None:

        return


    timestamp = float(
        record["timestamp"]
    )


    packet_size = int(
        record["packet_size"]
    )


    with live_lock:

        live_packets.append(record)


        live_capture_count += 1

        live_capture_bytes += packet_size


        source_port = record["source_port"]

        destination_port = record["destination_port"]


        if source_port is None:

            source_port = 0


        if destination_port is None:

            destination_port = 0


        flow_record = {

            "flow_id": None,

            "source_ip": record["source_ip"],

            "destination_ip": record["destination_ip"],

            "source_port": int(source_port),

            "destination_port": int(destination_port),

            "protocol": record["protocol"],

            "packet_count": 1,

            "total_bytes": packet_size,

            "duration": 0,

            "average_packet_size": packet_size,

            "packets_per_second": 0,

            "bytes_per_second": 0

        }


        key = create_flow_key(record)


        if key not in live_flows:

            live_flows[key] = {

                **flow_record,

                "start_time": timestamp,

                "end_time": timestamp

            }


        else:

            flow = live_flows[key]


            flow["packet_count"] += 1


            flow["total_bytes"] += packet_size


            if timestamp < flow["start_time"]:

                flow["start_time"] = timestamp


            if timestamp > flow["end_time"]:

                flow["end_time"] = timestamp


            duration = (

                flow["end_time"]

                - flow["start_time"]

            )


            flow["duration"] = duration


            flow["average_packet_size"] = (

                flow["total_bytes"]

                / flow["packet_count"]

            )


            if duration > 0:

                flow["packets_per_second"] = (

                    flow["packet_count"]

                    / duration

                )


                flow["bytes_per_second"] = (

                    flow["total_bytes"]

                    / duration

                )


        if len(live_flows) > MAX_LIVE_FLOWS:

            oldest_key = next(

                iter(live_flows)

            )


            del live_flows[oldest_key]


def start_capture(interface):

    global live_sniffer


    if live_sniffer is not None:

        return


    sniffer = AsyncSniffer(

        iface=(

            None

            if interface == "Default Interface"

            else interface

        ),

        prn=packet_callback,

        store=False

    )


    sniffer.start()


    live_sniffer = sniffer


def stop_capture():

    global live_sniffer


    if live_sniffer is None:

        return


    try:

        live_sniffer.stop()


    except Exception:

        pass


    live_sniffer = None


def is_capture_running():

    return live_sniffer is not None


def clear_live_data():

    global live_capture_count

    global live_capture_bytes


    with live_lock:

        live_packets.clear()

        live_flows.clear()


        live_capture_count = 0

        live_capture_bytes = 0


def format_bytes(value):

    value = float(value)


    if value < 1024:

        return f"{value:.0f} B"


    if value < 1024 * 1024:

        return f"{value / 1024:.2f} KB"


    if value < 1024 * 1024 * 1024:

        return f"{value / (1024 * 1024):.2f} MB"


    return f"{value / (1024 * 1024 * 1024):.2f} GB"


def get_live_statistics():

    with live_lock:

        packets = list(
            live_packets
        )


        flows = list(
            live_flows.values()
        )


        capture_count = live_capture_count

        capture_bytes = live_capture_bytes


    retained_packets = len(
        packets
    )


    protocol_counts = {}

    category_counts = {}

    device_bytes = {}

    classified_flows = []


    for flow in flows:

        flow_copy = flow.copy()


        try:

            category = classify_flow(
                flow_copy
            )


        except Exception:

            category = "Other"


        flow_copy["category"] = category


        classified_flows.append(
            flow_copy
        )


        protocol = str(
            flow["protocol"]
        ).upper()


        protocol_counts[protocol] = (

            protocol_counts.get(
                protocol,
                0
            )

            + flow["total_bytes"]

        )


        category_counts[category] = (

            category_counts.get(
                category,
                0
            )

            + flow["total_bytes"]

        )


        source_ip = flow["source_ip"]

        destination_ip = flow["destination_ip"]


        if is_local_device(source_ip):

            device_bytes[source_ip] = (

                device_bytes.get(
                    source_ip,
                    0
                )

                + flow["total_bytes"]

            )


        if is_local_device(destination_ip):

            device_bytes[destination_ip] = (

                device_bytes.get(
                    destination_ip,
                    0
                )

                + flow["total_bytes"]

            )


    return (

        packets,

        classified_flows,

        retained_packets,

        capture_bytes,

        protocol_counts,

        category_counts,

        device_bytes,

        capture_count

    )


@st.fragment(
    run_every=LIVE_REFRESH_INTERVAL
)
def render_live_data():

    (

        packets,

        flows,

        retained_packets,

        total_bytes,

        protocol_counts,

        category_counts,

        device_bytes,

        capture_count

    ) = get_live_statistics()


    retained_flows = len(
        flows
    )


    active_devices = len(
        device_bytes
    )


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(

            "PACKETS CAPTURED",

            f"{capture_count:,}"

        )


    with col2:

        st.metric(

            "SESSION TRAFFIC",

            format_bytes(total_bytes)

        )


    with col3:

        st.metric(

            "RETAINED FLOWS",

            f"{retained_flows:,}"

        )


    with col4:

        st.metric(

            "LOCAL SOURCES",

            f"{active_devices:,}"

        )


    st.caption(

        f"{retained_packets:,} most recent packets retained "

        f"for detailed display (maximum {MAX_LIVE_PACKETS:,})"

    )


    st.divider()


    st.subheader("📊 Traffic Intelligence")


    col1, col2 = st.columns(2)


    with col1:

        st.markdown(

            "### Protocol Traffic"

        )


        if protocol_counts:

            protocol_data = dict(

                sorted(

                    protocol_counts.items(),

                    key=lambda item: item[1],

                    reverse=True

                )

            )


            st.bar_chart(

                protocol_data

            )


            st.caption(

                "Traffic volume across retained live flows"

            )


        else:

            st.info(

                "Waiting for network traffic..."

            )


    with col2:

        st.markdown(

            "### Traffic Categories"

        )


        if category_counts:

            category_data = dict(

                sorted(

                    category_counts.items(),

                    key=lambda item: item[1],

                    reverse=True

                )

            )


            st.bar_chart(

                category_data

            )


            st.caption(

                "Traffic volume by rule-based category"

            )


        else:

            st.info(

                "Waiting for classified flows..."

            )


    st.divider()


    st.subheader("💻 Active Local Sources")


    if device_bytes:

        device_data = dict(

            sorted(

                device_bytes.items(),

                key=lambda item: item[1],

                reverse=True

            )

        )


        device_table = []


        for device_ip, bytes_used in device_data.items():

            device_table.append({

                "Source IP": device_ip,

                "Traffic": format_bytes(

                    bytes_used

                )

            })


        st.dataframe(

            device_table[:10],

            width="stretch",

            hide_index=True

        )


    else:

        st.info(

            "No local network sources detected yet."

        )


    st.divider()


    st.subheader("🔗 Retained Flow Intelligence")


    if flows:

        flow_table = []


        for flow in sorted(

            flows,

            key=lambda item: item["total_bytes"],

            reverse=True

        )[:20]:

            flow_table.append({

                "Source": flow["source_ip"],

                "Destination": flow["destination_ip"],

                "Protocol": flow["protocol"],

                "Source Port": flow["source_port"],

                "Destination Port": flow["destination_port"],

                "Packets": flow["packet_count"],

                "Traffic": format_bytes(

                    flow["total_bytes"]

                ),

                "Duration": round(

                    flow["duration"],

                    3

                ),

                "Category": flow["category"]

            })


        st.dataframe(

            flow_table,

            width="stretch",

            hide_index=True

        )


    else:

        st.info(

            "No retained flows detected yet."

        )


    st.divider()


    st.subheader("📦 Recent Packets")


    if packets:

        display_packets = []


        for packet in reversed(packets):

            display_packets.append({

                "Time": str(

                    packet["timestamp"]

                ),

                "Source": packet["source_ip"],

                "Destination": packet["destination_ip"],

                "Protocol": packet["protocol"],

                "Source Port": packet["source_port"],

                "Destination Port": packet["destination_port"],

                "Size": packet["packet_size"]

            })


        st.dataframe(

            display_packets[:100],

            width="stretch",

            hide_index=True

        )


    else:

        st.info(

            "No packets captured yet."

        )


def render():

    # =========================================================
    # PAGE HEADER
    # =========================================================

    st.title(

        "📡 Live Network Monitor"

    )


    st.caption(

        "Real-time packet capture, flow intelligence "

        "and rule-based traffic analysis"

    )


    st.divider()


    # =========================================================
    # CAPTURE CONTROLS
    # =========================================================

    interfaces = get_if_list()


    interface_options = [

        "Default Interface"

    ] + interfaces


    selected_interface = st.selectbox(

        "Network Interface",

        interface_options

    )


    running = is_capture_running()


    col1, col2, col3 = st.columns(3)


    with col1:

        if not running:

            if st.button(

                "▶ Start Capture",

                width="stretch"

            ):

                try:

                    start_capture(

                        selected_interface

                    )


                    st.rerun()


                except Exception as error:

                    st.error(

                        f"Unable to start packet capture: {error}"

                    )


        else:

            if st.button(

                "⏹ Stop Capture",

                width="stretch"

            ):

                stop_capture()


                st.rerun()


    with col2:

        if st.button(

            "🗑 Clear Live Data",

            width="stretch"

        ):

            clear_live_data()


            st.rerun()


    with col3:

        if running:

            st.success(

                "● CAPTURE RUNNING"

            )

        else:

            st.info(

                "● CAPTURE STOPPED"

            )


    st.divider()


    if running:

        st.caption(

            "Live capture is active. "

            "Statistics refresh automatically every second."

        )


    else:

        st.caption(

            "Capture is stopped. "

            "Select an interface and start capture."

        )


    render_live_data()