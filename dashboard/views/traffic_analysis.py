import pandas as pd

import plotly.express as px

import streamlit as st


from dashboard.views.common import (
    format_bytes,
    load_classified_data,
    get_high_volume_flows
)


# =============================================================
# DATA HELPERS
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

    data["destination_ip"] = (
        data["destination_ip"]
        .astype(str)
        .str.strip()
    )

    data["destination_port"] = pd.to_numeric(
        data["destination_port"],
        errors="coerce"
    ).fillna(0).astype(int)

    data["total_bytes"] = pd.to_numeric(
        data["total_bytes"],
        errors="coerce"
    ).fillna(0)

    data["packet_count"] = pd.to_numeric(
        data["packet_count"],
        errors="coerce"
    ).fillna(0)

    if "duration" in data.columns:
        data["duration"] = pd.to_numeric(
            data["duration"],
            errors="coerce"
        ).fillna(0)

    if "bytes_per_second" in data.columns:
        data["bytes_per_second"] = pd.to_numeric(
            data["bytes_per_second"],
            errors="coerce"
        ).fillna(0)

    return data


# =============================================================
# CHARTS
# =============================================================

def create_ranked_bar_chart(
    dataframe,
    label_column,
    value_column,
    height=350
):

    chart_data = dataframe.copy()

    chart_data[label_column] = (
        chart_data[label_column]
        .astype(str)
    )

    chart_data["display_value"] = (
        chart_data[value_column]
        .apply(format_bytes)
    )

    chart_data = chart_data.sort_values(
        value_column,
        ascending=True
    )

    figure = px.bar(
        chart_data,
        x=value_column,
        y=label_column,
        orientation="h",
        text="display_value"
    )

    figure.update_traces(
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Traffic: %{text}"
            "<extra></extra>"
        )
    )

    figure.update_layout(
        height=height,
        margin=dict(
            l=15,
            r=80,
            t=10,
            b=45
        ),
        xaxis=dict(
            title=None,
            showgrid=True,
            showticklabels=False,
            zeroline=False
        ),
        yaxis=dict(
            title=None,
            type="category",
            categoryorder="array",
            categoryarray=chart_data[label_column].tolist()
        ),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    return figure


# =============================================================
# RENDER
# =============================================================

def render():

    # ---------------------------------------------------------
    # Remove excessive Streamlit top spacing
    # ---------------------------------------------------------

    st.markdown(
        """
        <style>

        [data-testid="stAppViewBlockContainer"] {
            padding-top: 0.8rem !important;
        }

        .main .block-container {
            padding-top: 0.8rem !important;
        }

        h1 {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


    # ---------------------------------------------------------
    # Load data
    # ---------------------------------------------------------

    try:

        classified_df = load_classified_data()

    except Exception as error:

        st.error(
            f"Unable to load classified traffic data: {error}"
        )

        return


    if classified_df.empty:

        st.title("📊 Traffic Analysis")

        st.caption(
            "Detailed investigation of classified network traffic"
        )

        st.divider()

        st.info(
            "No classified traffic data is currently available."
        )

        return


    data = prepare_data(
        classified_df
    )


    # =========================================================
    # PAGE HEADER
    # =========================================================

    st.title("📊 Traffic Analysis")

    st.caption(
        "Detailed investigation of network traffic, "
        "destinations, ports and high-volume activity"
    )

    st.divider()


    # =========================================================
    # TRAFFIC FILTERS
    # =========================================================

    st.subheader("🔎 Traffic Filters")

    filter_col1, filter_col2, filter_col3 = st.columns(
        [1.35, 1, 1]
    )


    categories = sorted(
        data["category"].unique().tolist()
    )

    protocols = sorted(
        data["protocol"].unique().tolist()
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
            "Flow Ranking",
            [
                "Traffic Volume",
                "Packet Count",
                "Flow Duration"
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


    # =========================================================
    # SORTING
    # =========================================================

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

    elif "duration" in filtered_data.columns:

        filtered_data = filtered_data.sort_values(
            "duration",
            ascending=False
        )


    # =========================================================
    # TRAFFIC METRICS
    # =========================================================

    st.subheader("📌 Traffic Metrics")

    total_flows = len(
        filtered_data
    )

    total_bytes = int(
        filtered_data["total_bytes"].sum()
    )

    total_packets = int(
        filtered_data["packet_count"].sum()
    )

    destination_count = (
        filtered_data["destination_ip"]
        .nunique()
    )


    metric1, metric2, metric3, metric4 = st.columns(4)


    with metric1:

        st.metric(
            "FILTERED FLOWS",
            f"{total_flows:,}"
        )

        st.caption(
            "Classified network flows"
        )


    with metric2:

        st.metric(
            "TRAFFIC VOLUME",
            format_bytes(total_bytes)
        )

        st.caption(
            "Total captured bytes"
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
            "DESTINATIONS",
            f"{destination_count:,}"
        )

        st.caption(
            "Unique destination addresses"
        )


    # =========================================================
    # DESTINATION INTELLIGENCE
    # =========================================================

    st.divider()

    st.subheader("🎯 Destination Intelligence")


    if not filtered_data.empty:

        destination_data = (
            filtered_data
            .groupby("destination_ip")["total_bytes"]
            .sum()
            .sort_values(
                ascending=False
            )
            .head(10)
            .reset_index()
        )

        destination_data.columns = [
            "Destination",
            "Bytes"
        ]


        destination_col1, destination_col2 = st.columns(
            [1.55, 1]
        )


        with destination_col1:

            with st.container(border=True):

                st.markdown(
                    "### Top Destinations"
                )

                st.caption(
                    "Highest-volume destination addresses"
                )

                destination_chart = (
                    create_ranked_bar_chart(
                        destination_data,
                        "Destination",
                        "Bytes",
                        height=340
                    )
                )

                st.plotly_chart(
                    destination_chart,
                    width="stretch",
                    config={
                        "displayModeBar": False,
                        "responsive": True
                    }
                )


        with destination_col2:

            with st.container(border=True):

                st.markdown(
                    "### Destination Details"
                )

                destination_table = (
                    destination_data.copy()
                )

                destination_table["Traffic"] = (
                    destination_table["Bytes"]
                    .apply(format_bytes)
                )

                destination_table = (
                    destination_table[
                        [
                            "Destination",
                            "Traffic"
                        ]
                    ]
                )

                st.dataframe(
                    destination_table,
                    width="stretch",
                    hide_index=True,
                    height=340
                )


    else:

        st.info(
            "No destination traffic matches the selected filters."
        )


    # =========================================================
    # PORT INTELLIGENCE
    # =========================================================

    st.divider()

    st.subheader("🔌 Port Intelligence")


    if not filtered_data.empty:

        port_data = (
            filtered_data
            .groupby("destination_port")["total_bytes"]
            .sum()
            .sort_values(
                ascending=False
            )
            .head(10)
            .reset_index()
        )

        port_data.columns = [
            "Port",
            "Bytes"
        ]

        port_data["Port"] = (
            port_data["Port"]
            .astype(int)
            .astype(str)
        )


        port_col1, port_col2 = st.columns(
            [1.55, 1]
        )


        with port_col1:

            with st.container(border=True):

                st.markdown(
                    "### Top Destination Ports"
                )

                st.caption(
                    "Ports receiving the highest traffic volume"
                )

                port_chart = (
                    create_ranked_bar_chart(
                        port_data,
                        "Port",
                        "Bytes",
                        height=340
                    )
                )

                st.plotly_chart(
                    port_chart,
                    width="stretch",
                    config={
                        "displayModeBar": False,
                        "responsive": True
                    }
                )


        with port_col2:

            with st.container(border=True):

                st.markdown(
                    "### Port Details"
                )

                port_table = port_data.copy()

                port_table["Traffic"] = (
                    port_table["Bytes"]
                    .apply(format_bytes)
                )

                port_table = (
                    port_table[
                        [
                            "Port",
                            "Traffic"
                        ]
                    ]
                )

                st.dataframe(
                    port_table,
                    width="stretch",
                    hide_index=True,
                    height=340
                )


    else:

        st.info(
            "No destination-port traffic matches the selected filters."
        )


    # =========================================================
    # HIGH-VOLUME TRAFFIC
    # =========================================================

    st.divider()

    st.subheader("🚀 High-Volume Traffic")


    high_volume = get_high_volume_flows(
        filtered_data
    )


    if not high_volume.empty:

        high_volume = high_volume.copy()

        high_volume["Traffic"] = (
            high_volume["total_bytes"]
            .apply(format_bytes)
        )

        if "bytes_per_second" in high_volume.columns:

            high_volume["Rate"] = (
                high_volume["bytes_per_second"]
                .apply(format_bytes)
                + "/s"
            )

        columns = [
            "flow_id",
            "source_ip",
            "destination_ip",
            "protocol",
            "category",
            "packet_count",
            "Traffic"
        ]

        if "Rate" in high_volume.columns:

            columns.append("Rate")


        high_volume = high_volume[
            [
                column
                for column in columns
                if column in high_volume.columns
            ]
        ]


        high_volume = high_volume.rename(
            columns={
                "flow_id": "Flow Id",
                "source_ip": "Source IP",
                "destination_ip": "Destination IP",
                "protocol": "Protocol",
                "category": "Category",
                "packet_count": "Packets",
                "Traffic": "Traffic",
                "Rate": "Rate"
            }
        )


        with st.container(border=True):

            st.caption(
                "Flows identified as high-volume by the "
                "rule-based classification engine"
            )

            st.dataframe(
                high_volume,
                width="stretch",
                hide_index=True
            )


    else:

        st.success(
            "No high-volume traffic was identified "
            "for the selected filters."
        )


    # =========================================================
    # CLASSIFIED FLOW DETAILS
    # =========================================================

    st.divider()

    st.subheader("📋 Classified Flow Details")


    if filtered_data.empty:

        st.info(
            "No flows match the selected filters."
        )

    else:

        flow_details = filtered_data.copy()

        flow_details["Traffic"] = (
            flow_details["total_bytes"]
            .apply(format_bytes)
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
            "Traffic"
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
                "packet_count": "Packet Count",
                "Traffic": "Traffic"
            }
        )


        with st.container(border=True):

            st.caption(
                f"Showing {len(flow_details):,} "
                "classified network flows"
            )

            st.dataframe(
                flow_details,
                width="stretch",
                hide_index=True
            )