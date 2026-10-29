import pandas as pd

import streamlit as st

from dashboard.views.common import (
    format_bytes,
    load_classified_data
)


# =============================================================
# ALERT RULES
# =============================================================

HIGH_VOLUME_CATEGORIES = {
    "High Volume HTTPS",
    "High Volume TCP",
    "High Volume UDP"
}

LARGE_FLOW_BYTES = 50 * 1024
HIGH_PACKET_RATE = 100
LONG_FLOW_DURATION = 30


# =============================================================
# DATA PREPARATION
# =============================================================

def prepare_data(dataframe):

    data = dataframe.copy()

    data["category"] = (
        data["category"]
        .astype(str)
        .str.strip()
    )

    data["protocol"] = (
        data["protocol"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    data["source_ip"] = (
        data["source_ip"]
        .astype(str)
        .str.strip()
    )

    data["destination_ip"] = (
        data["destination_ip"]
        .astype(str)
        .str.strip()
    )

    numeric_columns = [
        "total_bytes",
        "packet_count",
        "duration",
        "bytes_per_second",
        "packets_per_second"
    ]

    for column in numeric_columns:

        if column in data.columns:

            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            ).fillna(0)

    return data


# =============================================================
# ALERT GENERATION
# =============================================================

def generate_alerts(data):

    alerts = []

    for _, flow in data.iterrows():

        flow_id = flow.get("flow_id", "-")
        source_ip = flow.get("source_ip", "-")
        destination_ip = flow.get(
            "destination_ip",
            "-"
        )

        protocol = flow.get(
            "protocol",
            "-"
        )

        category = flow.get(
            "category",
            "Other"
        )

        total_bytes = float(
            flow.get(
                "total_bytes",
                0
            )
        )

        packet_count = float(
            flow.get(
                "packet_count",
                0
            )
        )

        duration = float(
            flow.get(
                "duration",
                0
            )
        )

        bytes_per_second = float(
            flow.get(
                "bytes_per_second",
                0
            )
        )

        packets_per_second = float(
            flow.get(
                "packets_per_second",
                0
            )
        )

        # -----------------------------------------------------
        # HIGH VOLUME CLASSIFICATION
        # -----------------------------------------------------

        if category in HIGH_VOLUME_CATEGORIES:

            alerts.append({
                "Severity": "HIGH",
                "Alert": "High Volume Traffic",
                "Flow Id": flow_id,
                "Source IP": source_ip,
                "Destination IP": destination_ip,
                "Protocol": protocol,
                "Category": category,
                "Traffic": format_bytes(
                    total_bytes
                ),
                "Details": (
                    "Flow classified as high-volume "
                    "by the rule-based engine."
                )
            })

        # -----------------------------------------------------
        # LARGE FLOW
        # -----------------------------------------------------

        if total_bytes >= LARGE_FLOW_BYTES:

            alerts.append({
                "Severity": "MEDIUM",
                "Alert": "Large Traffic Flow",
                "Flow Id": flow_id,
                "Source IP": source_ip,
                "Destination IP": destination_ip,
                "Protocol": protocol,
                "Category": category,
                "Traffic": format_bytes(
                    total_bytes
                ),
                "Details": (
                    f"Flow exceeded the "
                    f"{format_bytes(LARGE_FLOW_BYTES)} "
                    "traffic threshold."
                )
            })

        # -----------------------------------------------------
        # HIGH PACKET RATE
        # -----------------------------------------------------

        if packets_per_second >= HIGH_PACKET_RATE:

            alerts.append({
                "Severity": "MEDIUM",
                "Alert": "High Packet Rate",
                "Flow Id": flow_id,
                "Source IP": source_ip,
                "Destination IP": destination_ip,
                "Protocol": protocol,
                "Category": category,
                "Traffic": format_bytes(
                    total_bytes
                ),
                "Details": (
                    f"Packet rate reached "
                    f"{packets_per_second:.2f} packets/s."
                )
            })

        # -----------------------------------------------------
        # LONG-LIVED FLOW
        # -----------------------------------------------------

        if duration >= LONG_FLOW_DURATION:

            alerts.append({
                "Severity": "LOW",
                "Alert": "Long-Lived Flow",
                "Flow Id": flow_id,
                "Source IP": source_ip,
                "Destination IP": destination_ip,
                "Protocol": protocol,
                "Category": category,
                "Traffic": format_bytes(
                    total_bytes
                ),
                "Details": (
                    f"Flow remained active for "
                    f"{duration:.2f} seconds."
                )
            })

    return pd.DataFrame(alerts)


# =============================================================
# ALERT SUMMARY
# =============================================================

def get_alert_summary(alerts):

    if alerts.empty:

        return {
            "total": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }

    return {
        "total": len(alerts),
        "high": int(
            (alerts["Severity"] == "HIGH").sum()
        ),
        "medium": int(
            (alerts["Severity"] == "MEDIUM").sum()
        ),
        "low": int(
            (alerts["Severity"] == "LOW").sum()
        )
    }


# =============================================================
# RENDER
# =============================================================

def render():

    # ---------------------------------------------------------
    # Load classified network data
    # ---------------------------------------------------------

    try:

        classified_df = load_classified_data()

    except Exception as error:

        st.error(
            f"Unable to load classified traffic data: {error}"
        )

        return

    # ---------------------------------------------------------
    # Empty state
    # ---------------------------------------------------------

    if classified_df.empty:

        st.title("⚠️ Network Alerts")

        st.caption(
            "Rule-based detection of unusual and "
            "high-volume network activity"
        )

        st.divider()

        st.info(
            "No classified network traffic is currently "
            "available for alert analysis."
        )

        return

    data = prepare_data(
        classified_df
    )

    alerts = generate_alerts(
        data
    )

    summary = get_alert_summary(
        alerts
    )

    # =========================================================
    # PAGE HEADER
    # =========================================================

    st.title("⚠️ Network Alerts")

    st.caption(
        "Rule-based detection of high-volume, "
        "large, high-rate and long-lived network flows"
    )

    st.divider()

    # =========================================================
    # ALERT SUMMARY
    # =========================================================

    st.subheader("📌 Alert Summary")

    metric1, metric2, metric3, metric4 = st.columns(4)

    with metric1:

        st.metric(
            "TOTAL ALERTS",
            f"{summary['total']:,}"
        )

        st.caption(
            "Detected network events"
        )

    with metric2:

        st.metric(
            "HIGH",
            f"{summary['high']:,}"
        )

        st.caption(
            "High-volume activity"
        )

    with metric3:

        st.metric(
            "MEDIUM",
            f"{summary['medium']:,}"
        )

        st.caption(
            "Elevated traffic activity"
        )

    with metric4:

        st.metric(
            "LOW",
            f"{summary['low']:,}"
        )

        st.caption(
            "Informational activity"
        )

    # =========================================================
    # ALERT FILTER
    # =========================================================

    st.divider()

    st.subheader("🔎 Alert Filters")

    if alerts.empty:

        st.success(
            "No network alerts were detected "
            "for the current classified traffic."
        )

        return

    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:

        severity_options = [
            "All",
            "HIGH",
            "MEDIUM",
            "LOW"
        ]

        selected_severity = st.selectbox(
            "Severity",
            severity_options
        )

    with filter_col2:

        alert_types = [
            "All"
        ] + sorted(
            alerts["Alert"]
            .unique()
            .tolist()
        )

        selected_alert = st.selectbox(
            "Alert Type",
            alert_types
        )

    filtered_alerts = alerts.copy()

    if selected_severity != "All":

        filtered_alerts = filtered_alerts[
            filtered_alerts["Severity"]
            == selected_severity
        ]

    if selected_alert != "All":

        filtered_alerts = filtered_alerts[
            filtered_alerts["Alert"]
            == selected_alert
        ]

    # =========================================================
    # ALERT TABLE
    # =========================================================

    st.divider()

    st.subheader("🚨 Detected Network Events")

    if filtered_alerts.empty:

        st.info(
            "No alerts match the selected filters."
        )

        return

    display_alerts = filtered_alerts[
        [
            "Severity",
            "Alert",
            "Flow Id",
            "Source IP",
            "Destination IP",
            "Protocol",
            "Category",
            "Traffic"
        ]
    ].copy()

    with st.container(border=True):

        st.caption(
            f"Showing {len(display_alerts):,} "
            "detected network events"
        )

        st.dataframe(
            display_alerts,
            width="stretch",
            hide_index=True
        )

    # =========================================================
    # ALERT DETAILS
    # =========================================================

    st.divider()

    st.subheader("📋 Alert Details")

    selected_flow = st.selectbox(
        "Select Alert",
        range(len(filtered_alerts)),
        format_func=lambda index: (
            f"{filtered_alerts.iloc[index]['Severity']} • "
            f"{filtered_alerts.iloc[index]['Alert']} • "
            f"Flow {filtered_alerts.iloc[index]['Flow Id']}"
        )
    )

    alert = filtered_alerts.iloc[
        selected_flow
    ]

    detail_col1, detail_col2 = st.columns(2)

    with detail_col1:

        with st.container(border=True):

            st.markdown(
                "### Event Information"
            )

            st.write(
                f"**Severity:** {alert['Severity']}"
            )

            st.write(
                f"**Alert:** {alert['Alert']}"
            )

            st.write(
                f"**Flow ID:** {alert['Flow Id']}"
            )

            st.write(
                f"**Category:** {alert['Category']}"
            )

    with detail_col2:

        with st.container(border=True):

            st.markdown(
                "### Network Information"
            )

            st.write(
                f"**Source:** {alert['Source IP']}"
            )

            st.write(
                f"**Destination:** "
                f"{alert['Destination IP']}"
            )

            st.write(
                f"**Protocol:** {alert['Protocol']}"
            )

            st.write(
                f"**Traffic:** {alert['Traffic']}"
            )

    with st.container(border=True):

        st.markdown(
            "### Detection Reason"
        )

        st.caption(
            alert["Details"]
        )

    # =========================================================
    # RULE CONFIGURATION
    # =========================================================

    st.divider()

    st.subheader("⚙️ Detection Rules")

    rule_data = pd.DataFrame(
        [
            {
                "Rule": "High Volume Traffic",
                "Condition": (
                    "High Volume HTTPS / TCP / UDP category"
                ),
                "Severity": "HIGH"
            },
            {
                "Rule": "Large Traffic Flow",
                "Condition": (
                    f"Traffic ≥ "
                    f"{format_bytes(LARGE_FLOW_BYTES)}"
                ),
                "Severity": "MEDIUM"
            },
            {
                "Rule": "High Packet Rate",
                "Condition": (
                    f"Packet rate ≥ "
                    f"{HIGH_PACKET_RATE} packets/s"
                ),
                "Severity": "MEDIUM"
            },
            {
                "Rule": "Long-Lived Flow",
                "Condition": (
                    f"Duration ≥ "
                    f"{LONG_FLOW_DURATION} seconds"
                ),
                "Severity": "LOW"
            }
        ]
    )

    with st.container(border=True):

        st.caption(
            "Deterministic rules used by the NetScope "
            "alert engine"
        )

        st.dataframe(
            rule_data,
            width="stretch",
            hide_index=True
        )