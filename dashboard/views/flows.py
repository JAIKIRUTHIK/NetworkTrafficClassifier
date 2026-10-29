import pandas as pd

import plotly.express as px

import streamlit as st


from dashboard.views.common import (
    format_bytes,
    load_classified_data
)


def prepare_data(dataframe):

    data = dataframe.copy()

    numeric_columns = [
        "flow_id",
        "source_port",
        "destination_port",
        "packet_count",
        "total_bytes",
        "duration",
        "average_packet_size",
        "packets_per_second",
        "bytes_per_second"
    ]

    for column in numeric_columns:

        if column in data.columns:

            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            ).fillna(0)

    for column in [
        "source_ip",
        "destination_ip",
        "protocol",
        "category"
    ]:

        if column in data.columns:

            data[column] = (
                data[column]
                .astype(str)
                .str.strip()
            )

    return data


def create_flow_chart(dataframe):

    chart_data = dataframe.copy()

    chart_data = (
        chart_data
        .sort_values(
            "total_bytes",
            ascending=True
        )
        .tail(10)
        .copy()
    )

    chart_data["Flow"] = (
        "Flow "
        + chart_data["flow_id"].astype(int).astype(str)
    )

    chart_data["Traffic"] = (
        chart_data["total_bytes"]
        .apply(format_bytes)
    )

    chart_data["Connection"] = (
        chart_data["source_ip"]
        + ":"
        + chart_data["source_port"].astype(int).astype(str)
        + " → "
        + chart_data["destination_ip"]
        + ":"
        + chart_data["destination_port"].astype(int).astype(str)
    )

    figure = px.bar(
        chart_data,
        x="total_bytes",
        y="Flow",
        orientation="h",
        text="Traffic"
    )

    figure.update_traces(
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Connection: %{customdata[1]}<br>"
            "Traffic: %{text}<br>"
            "Packets: %{customdata[2]}<br>"
            "Protocol: %{customdata[3]}<br>"
            "Category: %{customdata[4]}"
            "<extra></extra>"
        ),
        customdata=chart_data[
            [
                "flow_id",
                "Connection",
                "packet_count",
                "protocol",
                "category"
            ]
        ].values
    )

    figure.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=90,
            t=10,
            b=35
        ),
        xaxis=dict(
            title=None,
            showgrid=True,
            showticklabels=False,
            zeroline=False
        ),
        yaxis=dict(
            title=None,
            categoryorder="array",
            categoryarray=chart_data["Flow"].tolist()
        ),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    return figure


def render():

    try:

        classified_df = load_classified_data()

    except Exception as error:

        st.error(
            f"Unable to load flow data: {error}"
        )

        return

    if classified_df.empty:

        st.title("🔗 Flow Intelligence")

        st.caption(
            "Reconstructed network connections, "
            "traffic behavior and flow-level analytics"
        )

        st.divider()

        st.info(
            "No classified flow data is currently available."
        )

        return

    data = prepare_data(
        classified_df
    )

    # =========================================================
    # PAGE HEADER
    # =========================================================

    st.title("🔗 Flow Intelligence")

    st.caption(
        "Reconstructed network connections, "
        "traffic behavior and flow-level analytics"
    )

    st.divider()

    # =========================================================
    # FLOW FILTERS
    # =========================================================

    st.subheader("🔎 Flow Filters")

    filter_col1, filter_col2, filter_col3 = st.columns(
        [1.3, 1, 1]
    )

    categories = sorted(
        data["category"]
        .dropna()
        .unique()
        .tolist()
    )

    protocols = sorted(
        data["protocol"]
        .dropna()
        .unique()
        .tolist()
    )

    with filter_col1:

        selected_categories = st.multiselect(
            "Traffic Category",
            categories,
            default=categories
        )

    with filter_col2:

        selected_protocols = st.multiselect(
            "Protocol",
            protocols,
            default=protocols
        )

    with filter_col3:

        ranking = st.selectbox(
            "Sort Flows By",
            [
                "Traffic Volume",
                "Packet Count",
                "Duration"
            ]
        )

    filtered_data = data[
        data["category"].isin(
            selected_categories
        )
        &
        data["protocol"].isin(
            selected_protocols
        )
    ].copy()

    if ranking == "Traffic Volume":

        filtered_data = filtered_data.sort_values(
            "total_bytes",
            ascending=False
        )

    elif ranking == "Packet Count":

        filtered_data = filtered_data.sort_values(
            "packet_count",
            ascending=False
        )

    else:

        filtered_data = filtered_data.sort_values(
            "duration",
            ascending=False
        )

    # =========================================================
    # FLOW SUMMARY
    # =========================================================

    st.subheader("📌 Flow Summary")

    total_flows = len(
        filtered_data
    )

    total_bytes = int(
        filtered_data["total_bytes"].sum()
    )

    total_packets = int(
        filtered_data["packet_count"].sum()
    )

    average_duration = (
        filtered_data["duration"].mean()
        if not filtered_data.empty
        else 0
    )

    metric1, metric2, metric3, metric4 = st.columns(4)

    with metric1:

        st.metric(
            "TOTAL FLOWS",
            f"{total_flows:,}"
        )

        st.caption(
            "Reconstructed network connections"
        )

    with metric2:

        st.metric(
            "FLOW TRAFFIC",
            format_bytes(total_bytes)
        )

        st.caption(
            "Traffic represented by flows"
        )

    with metric3:

        st.metric(
            "PACKETS",
            f"{total_packets:,}"
        )

        st.caption(
            "Packets represented by flows"
        )

    with metric4:

        st.metric(
            "AVG. DURATION",
            f"{average_duration:.2f} s"
        )

        st.caption(
            "Average flow lifetime"
        )

    # =========================================================
    # FLOW ANALYTICS
    # =========================================================

    st.divider()

    st.subheader("📊 Flow Analytics")

    if not filtered_data.empty:

        col1, col2 = st.columns(
            [1.55, 1]
        )

        with col1:

            with st.container(border=True):

                st.markdown(
                    "### Highest Traffic Flows"
                )

                st.caption(
                    "Top network connections ranked by traffic volume"
                )

                chart_data = (
                    filtered_data
                    .head(10)
                    .copy()
                )

                figure = create_flow_chart(
                    chart_data
                )

                st.plotly_chart(
                    figure,
                    width="stretch",
                    config={
                        "displayModeBar": False,
                        "responsive": True
                    }
                )

        with col2:

            with st.container(border=True):

                st.markdown(
                    "### Flow Distribution"
                )

                st.caption(
                    "Traffic volume by flow protocol"
                )

                protocol_data = (
                    filtered_data
                    .groupby("protocol")["total_bytes"]
                    .sum()
                    .sort_values(
                        ascending=False
                    )
                    .reset_index()
                )

                protocol_data.columns = [
                    "Protocol",
                    "Bytes"
                ]

                protocol_data["Traffic"] = (
                    protocol_data["Bytes"]
                    .apply(format_bytes)
                )

                st.dataframe(
                    protocol_data[
                        [
                            "Protocol",
                            "Traffic"
                        ]
                    ],
                    width="stretch",
                    hide_index=True
                )

    else:

        st.info(
            "No flows match the selected filters."
        )

    # =========================================================
    # FLOW DETAILS
    # =========================================================

    st.divider()

    st.subheader("📋 Flow Details")

    if filtered_data.empty:

        st.info(
            "No flow details are available "
            "for the selected filters."
        )

    else:

        flow_details = filtered_data.copy()

        flow_details["Traffic"] = (
            flow_details["total_bytes"]
            .apply(format_bytes)
        )

        flow_details["Duration"] = (
            flow_details["duration"]
            .round(3)
            .astype(str)
            + " s"
        )

        columns = [
            "flow_id",
            "source_ip",
            "destination_ip",
            "source_port",
            "destination_port",
            "protocol",
            "category",
            "packet_count",
            "Traffic",
            "Duration"
        ]

        available_columns = [
            column
            for column in columns
            if column in flow_details.columns
        ]

        flow_details = flow_details[
            available_columns
        ]

        flow_details = flow_details.rename(
            columns={
                "flow_id": "Flow Id",
                "source_ip": "Source IP",
                "destination_ip": "Destination IP",
                "source_port": "Source Port",
                "destination_port": "Destination Port",
                "protocol": "Protocol",
                "category": "Category",
                "packet_count": "Packets",
                "Traffic": "Traffic",
                "Duration": "Duration"
            }
        )

        with st.container(border=True):

            st.caption(
                f"Showing {len(flow_details):,} "
                "reconstructed network flows"
            )

            st.dataframe(
                flow_details,
                width="stretch",
                hide_index=True
            )