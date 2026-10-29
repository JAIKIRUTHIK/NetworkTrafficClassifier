import plotly.express as px

import streamlit as st


from dashboard.views.common import (

    format_bytes,

    get_network_statistics,

    get_category_data,

    get_protocol_data,

    get_top_devices

)


def render_status_card(

    label,

    value,

    description,

    icon

):

    with st.container(border=True):

        st.caption(label)


        st.markdown(

            f"### {icon} {value}"

        )


        st.caption(

            description

        )


def create_donut_chart(

    dataframe,

    name_column,

    value_column,

    height=320

):

    figure = px.pie(

        dataframe,

        names=name_column,

        values=value_column,

        hole=0.58

    )


    figure.update_traces(

        textposition="inside",

        textinfo="percent",

        hovertemplate=(

            "<b>%{label}</b><br>"

            "Traffic: %{value}<br>"

            "Share: %{percent}"

            "<extra></extra>"

        )

    )


    figure.update_layout(

        height=height,

        margin=dict(

            l=10,

            r=10,

            t=10,

            b=10

        ),

        showlegend=True,

        legend=dict(

            orientation="v",

            yanchor="middle",

            y=0.5,

            xanchor="left",

            x=1.0,

            font=dict(

                size=11

            )

        ),

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)"

    )


    return figure


def create_device_chart(device_df):

    chart_data = device_df.copy()


    chart_data["Traffic"] = (

        chart_data["total_bytes"]

        .apply(format_bytes)

    )


    chart_data = chart_data.sort_values(

        "total_bytes",

        ascending=True

    )


    figure = px.bar(

        chart_data,

        x="total_bytes",

        y="device_ip",

        orientation="h",

        text="Traffic"

    )


    max_traffic = (

        chart_data["total_bytes"].max()

        if not chart_data.empty

        else 0

    )


    figure.update_traces(

        hovertemplate=(

            "<b>%{y}</b><br>"

            "Traffic: %{text}"

            "<extra></extra>"

        ),

        textposition="outside",

        cliponaxis=False

    )


    figure.update_layout(

        height=320,

        margin=dict(

            l=10,

            r=110,

            t=10,

            b=10

        ),

        xaxis=dict(

            title=None,

            showgrid=True,

            showticklabels=False,

            range=[

                0,

                max_traffic * 1.20

            ] if max_traffic > 0 else None

        ),

        yaxis=dict(

            title=None

        ),

        showlegend=False,

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)"

    )


    return figure


def render(device_df, classified_df):

    stats = get_network_statistics(

        device_df,

        classified_df

    )


    category_df = get_category_data(

        device_df

    )


    protocol_data = get_protocol_data(

        classified_df

    )


    top_devices = get_top_devices(

        device_df,

        limit=10

    )


    # =========================================================
    # PAGE HEADER
    # =========================================================


    st.title(

        "🌐 Network Traffic Intelligence"

    )


    st.caption(

        "Network traffic visibility, rule-based classification, "

        "source activity and usage analytics"

    )


    st.divider()


    # =========================================================
    # SYSTEM STATUS
    # =========================================================


    col1, col2, col3 = st.columns(3)


    with col1:

        render_status_card(

            "SYSTEM STATUS",

            "Pipeline Operational",

            "Network analysis engine is ready",

            "🟢"

        )


    with col2:

        render_status_card(

            "DATA SOURCE",

            "Network Capture",

            "Latest processed capture dataset",

            "📡"

        )


    with col3:

        render_status_card(

            "CLASSIFICATION",

            "Rule-Based",

            "Deterministic traffic classification",

            "🔍"

        )


    # =========================================================
    # KEY NETWORK METRICS
    # =========================================================


    st.subheader(

        "📊 Network Overview"

    )


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(

            "NETWORK SOURCES",

            f"{stats['devices']:,}"

        )


        st.caption(

            "Unique source IP addresses"

        )


    with col2:

        st.metric(

            "NETWORK FLOWS",

            f"{stats['flows']:,}"

        )


        st.caption(

            "Reconstructed connections"

        )


    with col3:

        st.metric(

            "TOTAL TRAFFIC",

            format_bytes(stats["bytes"])

        )


        st.caption(

            "Captured traffic volume"

        )


    with col4:

        st.metric(

            "PACKETS",

            f"{stats['packets']:,}"

        )


        st.caption(

            "Packets processed"

        )


    st.divider()


    # =========================================================
    # TRAFFIC DISTRIBUTION
    # =========================================================


    st.subheader(

        "📈 Traffic Distribution"

    )


    col1, col2 = st.columns(2)


    with col1:

        with st.container(border=True):

            st.markdown(

                "### Traffic by Category"

            )


            st.caption(

                "Network usage grouped by classification"

            )


            if not category_df.empty:

                category_chart = create_donut_chart(

                    category_df,

                    "Category",

                    "Bytes"

                )


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

                    "No category traffic available."

                )


    with col2:

        with st.container(border=True):

            st.markdown(

                "### Protocol Distribution"

            )


            st.caption(

                "Traffic volume by network protocol"

            )


            if not protocol_data.empty:

                protocol_df = (

                    protocol_data

                    .reset_index()

                )


                protocol_df.columns = [

                    "Protocol",

                    "Bytes"

                ]


                protocol_chart = create_donut_chart(

                    protocol_df,

                    "Protocol",

                    "Bytes"

                )


                st.plotly_chart(

                    protocol_chart,

                    width="stretch",

                    config={

                        "displayModeBar": False,

                        "responsive": True

                    }

                )


            else:

                st.info(

                    "No protocol traffic available."

                )


    st.divider()


    # =========================================================
    # NETWORK SOURCE INTELLIGENCE
    # =========================================================


    st.subheader(

        "💻 Network Source Intelligence"

    )


    if not top_devices.empty:

        col1, col2 = st.columns(

            [1.7, 1]

        )


        with col1:

            with st.container(border=True):

                st.markdown(

                    "### Top Network Sources by Traffic"

                )


                st.caption(

                    "Source IPs generating the highest network traffic"

                )


                device_chart = create_device_chart(

                    top_devices

                )


                st.plotly_chart(

                    device_chart,

                    width="stretch",

                    config={

                        "displayModeBar": False,

                        "responsive": True

                    }

                )


        with col2:

            with st.container(border=True):

                st.markdown(

                    "### Highest Traffic Source"

                )


                top_device = top_devices.iloc[0]


                st.metric(

                    "SOURCE IP",

                    top_device["device_ip"]

                )


                st.markdown(

                    f"### {format_bytes(top_device['total_bytes'])}"

                )


                st.caption(

                    "Total traffic generated"

                )


                total_bytes = top_devices[

                    "total_bytes"

                ].sum()


                if total_bytes > 0:

                    share = (

                        top_device["total_bytes"]

                        / total_bytes

                        * 100

                    )


                    st.divider()


                    st.caption(

                        "Share among top 10 sources"

                    )


                    st.markdown(

                        f"### {share:.2f}%"

                    )


    else:

        st.info(

            "No network source traffic available."

        )


    # =========================================================
    # NETWORK SOURCE DETAILS
    # =========================================================


    if not top_devices.empty:

        with st.container(border=True):

            st.markdown(

                "### Network Source Traffic Details"

            )


            st.caption(

                "Traffic volume and reconstructed flows by source IP"

            )


            device_table = top_devices.copy()


            device_table["Traffic"] = (

                device_table["total_bytes"]

                .apply(format_bytes)

            )


            flow_map = (

                device_df

                .set_index("device_ip")[

                    "total_flows"

                ]

                .to_dict()

            )


            device_table["Flows"] = (

                device_table["device_ip"]

                .map(flow_map)

            )


            device_table = device_table[

                [

                    "device_ip",

                    "Flows",

                    "Traffic"

                ]

            ]


            device_table.columns = [

                "Source IP",

                "Flows",

                "Traffic"

            ]


            st.dataframe(

                device_table,

                width="stretch",

                hide_index=True

            )


    st.divider()


    # =========================================================
    # TRAFFIC SUMMARY
    # =========================================================


    st.subheader(

        "📋 Traffic Summary"

    )


    if not category_df.empty:

        summary = category_df.copy()


        total = summary["Bytes"].sum()


        if total > 0:

            summary["Traffic %"] = (

                summary["Bytes"]

                / total

                * 100

            )


            summary["Volume"] = (

                summary["Bytes"]

                .apply(format_bytes)

            )


            summary["Traffic"] = (

                summary["Traffic %"]

                .round(2)

                .astype(str)

                + "%"

            )


            summary = summary[

                [

                    "Category",

                    "Volume",

                    "Traffic"

                ]

            ]


            with st.container(border=True):

                st.dataframe(

                    summary,

                    width="stretch",

                    hide_index=True

                )


        else:

            st.info(

                "No traffic volume available."

            )


    else:

        st.info(

            "No traffic summary available."

        )