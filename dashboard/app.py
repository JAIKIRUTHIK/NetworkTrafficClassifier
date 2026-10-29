from pathlib import Path

import sys


from dashboard.views.alerts import (
    render as render_alerts
)


from dashboard.views.flows import (
    render as render_flows
)


ROOT_DIR = Path(__file__).resolve().parent.parent


if str(ROOT_DIR) not in sys.path:

    sys.path.insert(0, str(ROOT_DIR))


import streamlit as st


from dashboard.views.common import (
    load_device_data,
    load_classified_data,
    load_packet_data,
    load_flow_data,
    load_feature_data,
    load_summary_data
)


from dashboard.views.overview import render as render_overview

from dashboard.views.live_monitor import render as render_live_monitor

from dashboard.views.traffic_analysis import (
    render as render_traffic_analysis
)

from dashboard.views.devices import (
    render as render_devices
)


st.set_page_config(
    page_title="NetScope | Network Traffic Intelligence",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================================================
# GLOBAL DESIGN SYSTEM
# =============================================================

st.markdown(
    """
    <style>

    /* =========================================================
       ROOT
    ========================================================= */

    :root {
        --page-background: #f4f7fb;
        --surface: #ffffff;
        --surface-soft: #f8fafc;

        --border: #dfe5ec;
        --border-soft: #e9edf2;

        --text-primary: #172033;
        --text-secondary: #667085;
        --text-muted: #98a2b3;

        --accent: #1677ff;
        --success: #16a34a;

        --shadow-card:
            0 2px 8px rgba(16, 24, 40, 0.04);

        --shadow-card-hover:
            0 5px 16px rgba(16, 24, 40, 0.08);
    }


    html,
    body,
    [data-testid="stAppViewContainer"] {
        background-color: var(--page-background);
    }


    .stApp {
        background-color: var(--page-background);
        color: var(--text-primary);
    }


    /* =========================================================
       STREAMLIT HEADER
       Keep native Streamlit header visible.
    ========================================================= */

    [data-testid="stHeader"] {
        background-color: var(--page-background) !important;
        border-bottom: 1px solid transparent !important;
    }


    [data-testid="stToolbar"] {
        display: flex !important;
    }


    [data-testid="stDecoration"] {
        display: none !important;
    }


    /* =========================================================
       MAIN APPLICATION AREA

       IMPORTANT:
       The native Streamlit header occupies vertical space.
       Keep enough top padding so page content never moves
       underneath the header.
    ========================================================= */

    [data-testid="stAppViewContainer"] {
        background-color: var(--page-background);
    }


    [data-testid="stAppViewContainer"] > .main {
        background-color: var(--page-background);
    }


    [data-testid="stMain"] {
        background-color: var(--page-background);
    }


    [data-testid="stMainBlockContainer"] {
        width: 100% !important;
        max-width: none !important;

        padding-top: 4rem !important;
        padding-bottom: 3rem !important;

        margin-top: 0 !important;
    }


    [data-testid="stAppViewBlockContainer"] {
        width: 100% !important;
        max-width: none !important;

        padding-top: 4rem !important;
        padding-bottom: 3rem !important;

        margin-top: 0 !important;
    }


    .main {
        background-color: var(--page-background);
        margin-top: 0 !important;
    }


    .main .block-container {
        width: 100%;
        max-width: none;

        padding-top: 4rem !important;
        padding-bottom: 3rem;

        padding-left: 2.25rem;
        padding-right: 2.25rem;

        margin-top: 0 !important;
    }


    /* =========================================================
       PAGE TITLE
    ========================================================= */

    [data-testid="stMain"] h1,
    [data-testid="stMainBlockContainer"] h1,
    [data-testid="stAppViewBlockContainer"] h1 {

        margin-top: 0 !important;
        padding-top: 0 !important;

        color: var(--text-primary);
    }


    h1 {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }


    /* =========================================================
       SIDEBAR
    ========================================================= */

    section[data-testid="stSidebar"] {

        background-color: var(--surface);

        border-right: 1px solid var(--border);

        min-width: 280px;
        max-width: 280px;
    }


    section[data-testid="stSidebar"] > div {

        width: 280px;
    }


    [data-testid="stSidebar"] > div:first-child {

        padding: 1.6rem 1.25rem 1.5rem 1.25rem;
    }


    .sidebar-brand {

        display: flex;
        align-items: center;

        font-size: 24px;
        line-height: 1.2;

        font-weight: 800;

        color: var(--text-primary);

        letter-spacing: -0.5px;

        margin-bottom: 0.35rem;
    }


    .sidebar-subtitle {

        color: var(--text-secondary);

        font-size: 11px;
        line-height: 1.5;

        margin-bottom: 2rem;
    }


    .sidebar-section {

        color: #8a94a6;

        font-size: 10px;
        line-height: 1.2;

        font-weight: 750;

        letter-spacing: 0.9px;

        margin-top: 1rem;
        margin-bottom: 0.7rem;
    }


    /* =========================================================
       SIDEBAR NAVIGATION
    ========================================================= */

    [data-testid="stSidebar"] [data-testid="stRadio"] {

        width: 100%;
    }


    [data-testid="stSidebar"] [data-testid="stRadio"] > div {

        gap: 0.25rem;
    }


    [data-testid="stSidebar"] [data-testid="stRadio"] label {

        min-height: 40px;

        display: flex;
        align-items: center;

        padding: 0.35rem 0.7rem;

        border-radius: 8px;

        color: #475467;

        font-size: 13px;
        font-weight: 550;

        transition:
            background-color 0.15s ease,
            color 0.15s ease;
    }


    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {

        background-color: #f2f5f9;

        color: var(--text-primary);
    }


    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] {

        background-color: #eaf3ff;

        color: #1264d6;

        font-weight: 700;
    }


    /* =========================================================
       SIDEBAR STATUS
    ========================================================= */

    [data-testid="stSidebar"] [data-testid="stAlert"] {

        margin-top: 0.4rem;
        margin-bottom: 0.8rem;

        border-radius: 9px;

        font-size: 11px;
    }


    [data-testid="stSidebar"] .stCaption {

        color: var(--text-muted);

        font-size: 10px;
    }


    [data-testid="stSidebar"] .stMarkdown p {

        font-size: 12px;
    }


    /* =========================================================
       PAGE HEADER
    ========================================================= */

    .page-header {

        margin-bottom: 1.75rem;
    }


    .page-title {

        color: var(--text-primary);

        font-size: clamp(28px, 2.4vw, 36px);

        line-height: 1.15;

        font-weight: 800;

        letter-spacing: -0.9px;

        margin-bottom: 0.45rem;
    }


    .page-subtitle {

        color: var(--text-secondary);

        font-size: 13px;

        line-height: 1.55;

        max-width: 850px;
    }


    /* =========================================================
       SECTION TITLES
    ========================================================= */

    .section-title {

        color: var(--text-primary);

        font-size: 19px;

        line-height: 1.3;

        font-weight: 750;

        letter-spacing: -0.25px;

        margin-top: 1.7rem;
        margin-bottom: 0.95rem;
    }


    /* =========================================================
       METRIC CARDS
    ========================================================= */

    [data-testid="stMetric"] {

        background-color: var(--surface);

        border: 1px solid var(--border);

        border-radius: 11px;

        padding: 1.15rem 1.2rem;

        min-height: 108px;

        box-shadow: var(--shadow-card);
    }


    [data-testid="stMetric"]:hover {

        box-shadow: var(--shadow-card-hover);
    }


    [data-testid="stMetricLabel"] {

        color: var(--text-secondary);

        font-size: 11px;

        font-weight: 700;

        letter-spacing: 0.25px;
    }


    [data-testid="stMetricValue"] {

        color: var(--text-primary);

        font-size: 26px;

        line-height: 1.2;

        font-weight: 800;

        letter-spacing: -0.5px;
    }


    /* =========================================================
       GENERAL CARDS
    ========================================================= */

    [data-testid="stVerticalBlockBorderWrapper"] {

        background-color: var(--surface);

        border: 1px solid var(--border);

        border-radius: 11px;

        box-shadow: var(--shadow-card);
    }


    /* =========================================================
       BUTTONS
    ========================================================= */

    .stButton > button {

        min-height: 40px;

        border-radius: 8px;

        border: 1px solid #d4dce6;

        background-color: var(--surface);

        color: #344054;

        font-size: 12px;

        font-weight: 650;

        transition:
            background-color 0.15s ease,
            border-color 0.15s ease,
            box-shadow 0.15s ease;
    }


    .stButton > button:hover {

        background-color: #f8fafc;

        border-color: #aeb9c8;

        box-shadow:
            0 2px 6px rgba(16, 24, 40, 0.06);
    }


    .stButton > button:focus {

        box-shadow:
            0 0 0 2px rgba(22, 119, 255, 0.15);
    }


    /* =========================================================
       SELECTBOX
    ========================================================= */

    [data-testid="stSelectbox"] label {

        color: var(--text-secondary);

        font-size: 11px;

        font-weight: 650;
    }


    [data-testid="stSelectbox"] > div > div {

        background-color: var(--surface);

        border: 1px solid #d5dde7;

        border-radius: 8px;

        min-height: 40px;
    }


    /* =========================================================
       DATAFRAMES
    ========================================================= */

    [data-testid="stDataFrame"] {

        width: 100%;

        border: 1px solid var(--border);

        border-radius: 10px;

        overflow: hidden;

        background-color: var(--surface);
    }


    /* =========================================================
       CHARTS
    ========================================================= */

    [data-testid="stPlotlyChart"] {

        width: 100%;
    }


    /* =========================================================
       ALERTS
    ========================================================= */

    [data-testid="stAlert"] {

        border-radius: 9px;

        border-width: 1px;

        font-size: 12px;
    }


    /* =========================================================
       DIVIDERS
    ========================================================= */

    hr {

        border: none;

        border-top: 1px solid var(--border);

        margin-top: 1.2rem;
        margin-bottom: 1.2rem;
    }


    /* =========================================================
       CAPTIONS
    ========================================================= */

    [data-testid="stCaptionContainer"] {

        color: var(--text-secondary);
    }


    /* =========================================================
       FOOTER
    ========================================================= */

    .footer {

        color: var(--text-muted);

        font-size: 10px;

        line-height: 1.5;

        text-align: center;

        margin-top: 3rem;

        padding-top: 1.1rem;

        border-top: 1px solid var(--border);
    }


    /* =========================================================
       RESPONSIVE
    ========================================================= */

    @media (max-width: 1100px) {

        .main .block-container {

            padding-left: 1.5rem;
            padding-right: 1.5rem;

            padding-top: 4rem !important;
        }

        .page-title {

            font-size: 30px;
        }

    }


    @media (max-width: 768px) {

        .main .block-container {

            padding-left: 1rem;
            padding-right: 1rem;

            padding-top: 4rem !important;
        }

        .page-title {

            font-size: 27px;
        }

        .page-subtitle {

            font-size: 12px;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# =============================================================
# DATA LOADING
# =============================================================

def load_all_data():

    device_df = load_device_data()

    classified_df = load_classified_data()

    return device_df, classified_df


def get_pipeline_status():

    packet_df = load_packet_data()

    flow_df = load_flow_data()

    feature_df = load_feature_data()

    classified_df = load_classified_data()

    summary_df = load_summary_data()

    device_df = load_device_data()


    stages = [

        {
            "stage": "Packet Capture",
            "description": "Raw network packets captured and parsed",
            "file": "data/packets.csv",
            "records": len(packet_df),
            "unit": "IPv4 records"
        },

        {
            "stage": "Flow Reconstruction",
            "description": "Packets grouped into bidirectional network flows",
            "file": "data/flows.csv",
            "records": len(flow_df),
            "unit": "flows"
        },

        {
            "stage": "Feature Extraction",
            "description": "Flow-level traffic features calculated",
            "file": "data/flow_features.csv",
            "records": len(feature_df),
            "unit": "flows"
        },

        {
            "stage": "Traffic Classification",
            "description": "Flows classified using deterministic rules",
            "file": "data/classified_flows.csv",
            "records": len(classified_df),
            "unit": "flows"
        },

        {
            "stage": "Usage Analysis",
            "description": "Traffic usage aggregated by category and protocol",
            "file": "data/usage_summary.csv",
            "records": len(summary_df),
            "unit": "summary records"
        },

        {
            "stage": "Device Aggregation",
            "description": "Network traffic aggregated by source device",
            "file": "data/device_usage.csv",
            "records": len(device_df),
            "unit": "devices"
        }

    ]

    return stages


# =============================================================
# SIDEBAR
# =============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">
            🌐 NetScope
        </div>

        <div class="sidebar-subtitle">
            Network Traffic Intelligence Platform
        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown(
        '<div class="sidebar-section">NAVIGATION</div>',
        unsafe_allow_html=True
    )


    page = st.radio(
        "Navigation",
        [
            "Overview",
            "Live Monitor",
            "Traffic Analysis",
            "Devices",
            "Flows",
            "Alerts",
            "Pipeline Status"
        ],
        label_visibility="collapsed"
    )


    st.divider()


    st.markdown(
        '<div class="sidebar-section">SYSTEM STATUS</div>',
        unsafe_allow_html=True
    )


    st.success(
        "● ANALYSIS ENGINE ONLINE"
    )


    st.caption(
        "Classification Engine"
    )


    st.write(
        "Rule-Based"
    )


    st.caption(
        "Data Source"
    )


    st.write(
        "Network Capture"
    )


    st.divider()


    if st.button(
        "↻ Refresh Data",
        width="stretch"
    ):

        st.rerun()


    st.divider()


    st.caption(
        "NetScope v1.0"
    )

    st.caption(
        "Network Traffic Intelligence"
    )

    st.caption(
        "Rule-Based Analysis • No ML"
    )


# =============================================================
# LOAD DATA
# =============================================================

try:

    device_df, classified_df = load_all_data()

except Exception as error:

    st.error(
        f"Unable to load network data: {error}"
    )

    st.stop()


# =============================================================
# PAGE ROUTING
# =============================================================

if page == "Overview":

    render_overview(
        device_df,
        classified_df
    )


elif page == "Live Monitor":

    render_live_monitor()


elif page == "Traffic Analysis":

    render_traffic_analysis()


elif page == "Devices":

    render_devices()


elif page == "Flows":

    render_flows()


elif page == "Alerts":

    render_alerts()


elif page == "Pipeline Status":

    stages = get_pipeline_status()


    completed_stages = sum(
        1 for stage in stages
        if stage["records"] > 0
    )


    pipeline_operational = (
        completed_stages == len(stages)
    )


    st.title("⚙️ Pipeline Status")


    st.caption(
        "Network traffic processing stages, "
        "execution status and generated dataset health"
    )


    st.divider()


    col1, col2, col3 = st.columns(3)


    with col1:

        if pipeline_operational:

            st.metric(
                "PIPELINE STATUS",
                "Operational"
            )

        else:

            st.metric(
                "PIPELINE STATUS",
                "Incomplete"
            )


    with col2:

        st.metric(
            "PROCESSING STAGES",
            f"{completed_stages}/{len(stages)}"
        )


    with col3:

        st.metric(
            "DATA SOURCE",
            "Network Capture"
        )


    st.divider()


    st.subheader("📊 Processing Pipeline")


    st.caption(
        "Latest generated outputs from the NetScope analysis pipeline"
    )


    for index, stage in enumerate(stages, start=1):

        with st.container(border=True):

            col1, col2, col3 = st.columns([0.8, 4.2, 2])


            with col1:

                st.markdown(
                    f"### {index}"
                )


            with col2:

                st.markdown(
                    f"### {stage['stage']}"
                )


                st.caption(
                    stage["description"]
                )


                st.caption(
                    stage["file"]
                )


            with col3:

                if stage["records"] > 0:

                    st.success(
                        "✓ COMPLETED"
                    )


                    st.caption(
                        f"{stage['records']:,} {stage['unit']}"
                    )

                else:

                    st.warning(
                        "⚠ NO DATA"
                    )


                    st.caption(
                        f"0 {stage['unit']}"
                    )


    st.divider()


    st.subheader("📁 Generated Data")


    st.caption(
        "Files produced by the network traffic processing pipeline"
    )


    data_files = [

        (
            "Packet Records",
            "data/packets.csv",
            len(load_packet_data())
        ),

        (
            "Reconstructed Flows",
            "data/flows.csv",
            len(load_flow_data())
        ),

        (
            "Flow Features",
            "data/flow_features.csv",
            len(load_feature_data())
        ),

        (
            "Classified Flows",
            "data/classified_flows.csv",
            len(load_classified_data())
        ),

        (
            "Usage Summary",
            "data/usage_summary.csv",
            len(load_summary_data())
        ),

        (
            "Device Usage",
            "data/device_usage.csv",
            len(load_device_data())
        )

    ]


    data_table = []


    for name, file_path, records in data_files:

        data_table.append(
            {
                "Dataset": name,
                "File": file_path,
                "Records": records,
                "Status": "Available" if records > 0 else "Empty"
            }
        )


    st.dataframe(
        data_table,
        width="stretch",
        hide_index=True
    )


    st.divider()


    st.subheader("ℹ️ Pipeline Architecture")


    st.info(
        "Packet Capture → Flow Reconstruction → Feature Extraction "
        "→ Rule-Based Classification → Usage Analysis "
        "→ Device Aggregation"
    )


# =============================================================
# FOOTER
# =============================================================

st.markdown(
    """
    <div class="footer">
        NetScope — Network Traffic Intelligence Platform
        <br>
        Rule-Based Classification • Real Network Capture • No ML
    </div>
    """,
    unsafe_allow_html=True
)