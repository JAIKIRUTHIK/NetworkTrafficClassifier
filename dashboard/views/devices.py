import pandas as pd

import plotly.express as px

import streamlit as st


from dashboard.views.common import (

    format_bytes,

    load_device_data

)


# =============================================================
# DATA PREPARATION
# =============================================================


def prepare_device_data(device_df):

    data = device_df.copy()

    data["device_ip"] = (

        data["device_ip"]

        .astype(str)

        .str.strip()

    )


    data["total_flows"] = pd.to_numeric(

        data["total_flows"],

        errors="coerce"

    ).fillna(0)


    data["total_bytes"] = pd.to_numeric(

        data["total_bytes"],

        errors="coerce"

    ).fillna(0)


    category_columns = [

        column

        for column in data.columns

        if column not in {

            "device_ip",

            "total_flows",

            "total_bytes"

        }

    ]


    for column in category_columns:

        data[column] = pd.to_numeric(

            data[column],

            errors="coerce"

        ).fillna(0)


    def dominant_category(row):

        category_values = {

            column: row[column]

            for column in category_columns

            if row[column] > 0

        }


        if not category_values:

            return "Other"


        return max(

            category_values,

            key=category_values.get

        )


    data["dominant_category"] = data.apply(

        dominant_category,

        axis=1

    )


    data["traffic_share"] = 0.0


    total_bytes = data["total_bytes"].sum()


    if total_bytes > 0:

        data["traffic_share"] = (

            data["total_bytes"]

            / total_bytes

            * 100

        )


    return data


# =============================================================
# CHARTS
# =============================================================


def create_device_traffic_chart(device_df):

    chart_data = (

        device_df

        .sort_values(

            "total_bytes",

            ascending=True

        )

        .tail(10)

        .copy()

    )


    chart_data["Traffic"] = (

        chart_data["total_bytes"]

        .apply(format_bytes)

    )


    figure = px.bar(

        chart_data,

        x="total_bytes",

        y="device_ip",

        orientation="h",

        text="Traffic"

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

        height=390,

        margin=dict(

            l=10,

            r=75,

            t=15,

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

            type="category"

        ),

        showlegend=False,

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)"

    )


    return figure


def create_category_chart(device_df):

    category_columns = [

        column

        for column in device_df.columns

        if column not in {

            "device_ip",

            "total_flows",

            "total_bytes",

            "dominant_category",

            "traffic_share"

        }

    ]


    category_data = []


    for category in category_columns:

        value = device_df[category].sum()


        if value > 0:

            category_data.append({

                "Category": category,

                "Bytes": value

            })


    category_df = pd.DataFrame(

        category_data

    )


    if category_df.empty:

        return None


    category_df = (

        category_df

        .sort_values(

            "Bytes",

            ascending=False

        )

        .head(8)

    )


    category_df["Traffic"] = (

        category_df["Bytes"]

        .apply(format_bytes)

    )


    figure = px.bar(

        category_df,

        x="Bytes",

        y="Category",

        orientation="h",

        text="Traffic"

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

        height=390,

        margin=dict(

            l=10,

            r=75,

            t=15,

            b=35

        ),

        xaxis=dict(

            title=None,

            showgrid=True,

            showticklabels=False,

            zeroline=False

        ),

        yaxis=dict(

            title=None

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

    # =========================================================
    # LOAD DATA
    # =========================================================

    try:

        device_df = load_device_data()


    except Exception as error:

        st.error(

            f"Unable to load device data: {error}"

        )

        return


    if device_df.empty:

        st.title("💻 Device Intelligence")


        st.caption(

            "Device-level traffic usage, activity "

            "and network behavior"

        )


        st.divider()


        st.info(

            "No device usage data is currently available."

        )


        return


    data = prepare_device_data(

        device_df

    )


    # =========================================================
    # PAGE HEADER
    # =========================================================

    st.title("💻 Device Intelligence")


    st.caption(

        "Device-level traffic usage, activity, "

        "traffic distribution and network behavior"

    )


    st.divider()


    # =========================================================
    # DEVICE SUMMARY
    # =========================================================

    st.subheader("📌 Device Summary")


    total_devices = len(data)


    total_flows = int(

        data["total_flows"].sum()

    )


    total_bytes = int(

        data["total_bytes"].sum()

    )


    average_bytes = (

        total_bytes / total_devices

        if total_devices > 0

        else 0

    )


    highest_device = (

        data

        .sort_values(

            "total_bytes",

            ascending=False

        )

        .iloc[0]

    )


    metric1, metric2, metric3, metric4 = st.columns(4)


    with metric1:

        st.metric(

            "DEVICES",

            f"{total_devices:,}"

        )


        st.caption(

            "Unique network sources"

        )


    with metric2:

        st.metric(

            "DEVICE TRAFFIC",

            format_bytes(total_bytes)

        )


        st.caption(

            "Total traffic generated"

        )


    with metric3:

        st.metric(

            "FLOWS",

            f"{total_flows:,}"

        )


        st.caption(

            "Reconstructed connections"

        )


    with metric4:

        st.metric(

            "AVG. TRAFFIC / DEVICE",

            format_bytes(average_bytes)

        )


        st.caption(

            "Average device traffic"

        )


    # =========================================================
    # TOP DEVICE
    # =========================================================

    st.divider()


    st.subheader("🏆 Highest Traffic Device")


    with st.container(border=True):

        top_header_col1, top_header_col2 = st.columns([3, 1])


        with top_header_col1:

            st.markdown(

                "### Highest Traffic Source"

            )


            st.markdown(

                f"## {highest_device['device_ip']}"

            )


            st.caption(

                "Device generating the highest amount of observed network traffic"

            )


        with top_header_col2:

            st.metric(

                "TRAFFIC SHARE",

                f"{highest_device['traffic_share']:.2f}%"

            )


        st.divider()


        info_col1, info_col2, info_col3 = st.columns(3)


        with info_col1:

            st.metric(

                "TOTAL TRAFFIC",

                format_bytes(highest_device["total_bytes"])

            )


            st.caption(

                "Observed traffic"

            )


        with info_col2:

            st.metric(

                "TOTAL FLOWS",

                f"{int(highest_device['total_flows']):,}"

            )


            st.caption(

                "Reconstructed connections"

            )


        with info_col3:

            st.metric(

                "DOMINANT CATEGORY",

                highest_device["dominant_category"]

            )


            st.caption(

                "Primary traffic classification"

            )


    # =========================================================
    # DEVICE ANALYTICS
    # =========================================================

    st.divider()


    st.subheader("📊 Device Analytics")


    chart_col1, chart_col2 = st.columns(2)


    with chart_col1:

        with st.container(border=True):

            st.markdown(

                "### Device Traffic Ranking"

            )


            st.caption(

                "Top devices ranked by total traffic"

            )


            device_chart = create_device_traffic_chart(

                data

            )


            st.plotly_chart(

                device_chart,

                width="stretch",

                config={

                    "displayModeBar": False,

                    "responsive": True

                }

            )


    with chart_col2:

        with st.container(border=True):

            st.markdown(

                "### Traffic by Category"

            )


            st.caption(

                "Traffic generated across classification categories"

            )


            category_chart = create_category_chart(

                data

            )


            if category_chart is not None:

                st.plotly_chart(

                    category_chart,

                    width="stretch",

                    config={

                        "displayModeBar": False,

                        "responsive": True

                    }

                )


            else:

                st.info(

                    "No category traffic is available."

                )


    # =========================================================
    # DEVICE DETAILS
    # =========================================================

    st.divider()


    st.subheader("📋 Device Details")


    display_data = (

        data

        .sort_values(

            "total_bytes",

            ascending=False

        )

        .copy()

    )


    display_data["Traffic"] = (

        display_data["total_bytes"]

        .apply(format_bytes)

    )


    display_data["Traffic Share"] = (

        display_data["traffic_share"]

        .round(2)

        .astype(str)

        + "%"

    )


    display_data = display_data[

        [

            "device_ip",

            "total_flows",

            "Traffic",

            "Traffic Share",

            "dominant_category"

        ]

    ]


    display_data.columns = [

        "Device IP",

        "Flows",

        "Traffic",

        "Traffic Share",

        "Dominant Category"

    ]


    with st.container(border=True):

        st.caption(

            f"Showing {len(display_data):,} network devices"

        )


        st.dataframe(

            display_data,

            width="stretch",

            hide_index=True

        )