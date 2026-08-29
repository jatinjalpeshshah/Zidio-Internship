
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="Project Foresight",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================================================================
# CUSTOM CSS
# =============================================================================

st.markdown(
    """
    <style>

    .stApp {
        background: #0b0f14;
    }

    [data-testid="stSidebar"] {
        background: #171b24;
        border-right: 1px solid #2b313c;
    }

    [data-testid="stHeader"] {
        background: rgba(11, 15, 20, 0.95);
    }

    h1, h2, h3, h4 {
        color: #f8fafc;
        letter-spacing: -0.025em;
    }

    .hero-title {
        font-size: 46px;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1.05;
        margin-bottom: 6px;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 15px;
        margin-bottom: 24px;
    }

    .kpi-card {
        background: linear-gradient(
            145deg,
            #181e27,
            #11161e
        );
        border: 1px solid #2b313c;
        border-radius: 14px;
        padding: 18px;
        min-height: 110px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.16);
    }

    .kpi-label {
        color: #94a3b8;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 9px;
    }

    .kpi-value {
        color: #f8fafc;
        font-size: 27px;
        font-weight: 750;
        line-height: 1.1;
    }

    .kpi-note {
        color: #64748b;
        font-size: 10px;
        margin-top: 7px;
    }

    .callout {
        background: #151b24;
        border: 1px solid #303744;
        border-radius: 14px;
        padding: 17px 20px;
        margin: 18px 0 22px 0;
    }

    .callout-title {
        color: #f8fafc;
        font-weight: 700;
        font-size: 15px;
        margin-bottom: 5px;
    }

    .callout-text {
        color: #a8b3c2;
        font-size: 13px;
        line-height: 1.55;
    }

    .sidebar-brand {
        font-size: 23px;
        font-weight: 800;
        color: #f8fafc;
    }

    .sidebar-subtitle {
        color: #94a3b8;
        font-size: 12px;
        margin-top: 4px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =============================================================================
# PATHS
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

SKU_FILE = DATA_DIR / "dashboard_sku_summary.csv"
FORECAST_FILE = DATA_DIR / "dashboard_forecast_actual.csv"
CATEGORY_FILE = DATA_DIR / "dashboard_category_summary.csv"
KPI_FILE = DATA_DIR / "dashboard_kpi_summary.csv"


# =============================================================================
# DATA LOADING
# =============================================================================

@st.cache_data
def load_data():

    sku = pd.read_csv(SKU_FILE)
    forecast = pd.read_csv(FORECAST_FILE)
    category = pd.read_csv(CATEGORY_FILE)
    kpi = pd.read_csv(KPI_FILE)

    if "week_start" in forecast.columns:
        forecast["week_start"] = pd.to_datetime(
            forecast["week_start"],
            errors="coerce"
        )

    if "week_end" in forecast.columns:
        forecast["week_end"] = pd.to_datetime(
            forecast["week_end"],
            errors="coerce"
        )

    if len(kpi.columns) >= 2:

        kpi.columns = [
            str(c).strip().lower()
            for c in kpi.columns
        ]

        if "kpi" not in kpi.columns:
            kpi = kpi.iloc[:, :2].copy()
            kpi.columns = ["kpi", "value"]

    if "value" in kpi.columns:
        kpi["value"] = pd.to_numeric(
            kpi["value"],
            errors="coerce"
        )

    return sku, forecast, category, kpi


sku_df, forecast_df, category_df, kpi_df = load_data()


# =============================================================================
# COLUMN HELPERS
# =============================================================================

def has_col(df, name):
    return name in df.columns


def numeric_series(df, name, default=0):
    if name not in df.columns:
        return pd.Series(
            default,
            index=df.index,
            dtype="float64"
        )

    return pd.to_numeric(
        df[name],
        errors="coerce"
    ).fillna(default)


def text_series(df, name, default=""):
    if name not in df.columns:
        return pd.Series(
            default,
            index=df.index,
            dtype="object"
        )

    return df[name].fillna(default).astype(str)


def money(value):
    try:
        return f"₹{float(value):,.0f}"
    except Exception:
        return "₹0"


def num(value):
    try:
        return f"{float(value):,.0f}"
    except Exception:
        return "0"


def dec(value):
    try:
        return f"{float(value):,.2f}"
    except Exception:
        return "0.00"


def get_kpi(name, default=0):

    if "kpi" not in kpi_df.columns:
        return default

    matches = kpi_df[
        kpi_df["kpi"]
        .astype(str)
        .str.strip()
        .str.lower()
        == name.strip().lower()
    ]

    if len(matches) == 0:
        return default

    value = pd.to_numeric(
        matches["value"].iloc[0],
        errors="coerce"
    )

    if pd.isna(value):
        return default

    return float(value)


def kpi_card(label, value, note=""):

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def style_chart(fig, height=390):

    fig.update_layout(
        height=height,
        margin=dict(
            l=10,
            r=10,
            t=50,
            b=10
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#cbd5e1"
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)"
        )
    )

    fig.update_xaxes(
        gridcolor="#242b35"
    )

    fig.update_yaxes(
        gridcolor="#242b35"
    )

    return fig


# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">
            PROJECT FORESIGHT
        </div>
        <div class="sidebar-subtitle">
            Demand & Inventory Intelligence
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### Navigation")

    page = st.radio(
        "Dashboard",
        [
            "🏠 Executive Overview",
            "📈 Sales & Forecast",
            "⚠️ Inventory Risk",
            "📦 Replenishment",
            "🏷️ Overstock / Markdown",
            "🔎 SKU Explorer",
            "📊 Category Intelligence"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("### Global Filters")

    if "category" in sku_df.columns:

        categories = sorted(
            sku_df["category"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

    else:

        categories = []

    selected_categories = st.multiselect(
        "Category",
        categories,
        default=categories
    )

    risk_options = [
        x for x in ["Critical", "High", "Low"]
        if "risk_level" in sku_df.columns
    ]

    selected_risks = st.multiselect(
        "Risk Level",
        risk_options,
        default=risk_options
    )

    status_options = [
        x for x in ["SHORTAGE", "SURPLUS", "BALANCED"]
        if "inventory_status" in sku_df.columns
    ]

    selected_statuses = st.multiselect(
        "Inventory Status",
        status_options,
        default=status_options
    )


# =============================================================================
# FILTER DATA
# =============================================================================

filtered = sku_df.copy()

if selected_categories and "category" in filtered.columns:

    filtered = filtered[
        filtered["category"]
        .astype(str)
        .isin(selected_categories)
    ]

if selected_risks and "risk_level" in filtered.columns:

    filtered = filtered[
        filtered["risk_level"]
        .astype(str)
        .isin(selected_risks)
    ]

if selected_statuses and "inventory_status" in filtered.columns:

    filtered = filtered[
        filtered["inventory_status"]
        .astype(str)
        .isin(selected_statuses)
    ]


# =============================================================================
# HERO
# =============================================================================

st.markdown(
    """
    <div class="hero-title">
        PROJECT FORESIGHT
    </div>

    <div class="hero-subtitle">
        Demand Forecasting • Inventory Risk • Business Intelligence
    </div>
    """,
    unsafe_allow_html=True
)


# =============================================================================
# EXECUTIVE OVERVIEW
# =============================================================================

if page == "🏠 Executive Overview":

    st.markdown("## Executive Inventory Overview")

    st.caption(
        "High-level view of demand, inventory exposure, risk and recommended actions."
    )

    forecast_total = numeric_series(
        filtered,
        "forecast_demand"
    ).sum()

    actual_total = numeric_series(
        filtered,
        "actual_units"
    ).sum()

    stock_total = numeric_series(
        filtered,
        "stock_on_hand"
    ).sum()

    avg_risk = numeric_series(
        filtered,
        "inventory_risk_score"
    ).mean()

    critical = int(
        text_series(
            filtered,
            "risk_level"
        ).eq("Critical").sum()
    )

    shortage = int(
        text_series(
            filtered,
            "inventory_status"
        ).eq("SHORTAGE").sum()
    )

    replenishment = numeric_series(
        filtered,
        "recommended_replenishment_units"
    ).sum()

    sales_risk = numeric_series(
        filtered,
        "sales_value_at_risk"
    ).sum()

    capital_locked = numeric_series(
        filtered,
        "capital_locked_in_overstock"
    ).sum()

    wape = get_kpi(
        "overall_wape_percent"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card(
            "Total SKUs",
            num(len(filtered)),
            "Filtered SKU universe"
        )

    with c2:
        kpi_card(
            "Forecast Demand",
            num(forecast_total),
            "Forecast units"
        )

    with c3:
        kpi_card(
            "Actual Units",
            num(actual_total),
            "Actual demand"
        )

    with c4:
        kpi_card(
            "Stock on Hand",
            num(stock_total),
            "Available stock"
        )

    c5, c6, c7, c8 = st.columns(4)

    with c5:
        kpi_card(
            "Average Risk Score",
            dec(avg_risk),
            "Inventory risk score"
        )

    with c6:
        kpi_card(
            "Critical SKUs",
            num(critical),
            "Immediate attention"
        )

    with c7:
        kpi_card(
            "Shortage SKUs",
            num(shortage),
            "Demand exceeds stock"
        )

    with c8:
        kpi_card(
            "Replenishment Units",
            num(replenishment),
            "Recommended quantity"
        )

    c9, c10 = st.columns(2)

    with c9:
        kpi_card(
            "Sales Value at Risk",
            money(sales_risk),
            "Calculated business exposure"
        )

    with c10:
        kpi_card(
            "Capital Locked",
            money(capital_locked),
            "Excess inventory value"
        )

    st.markdown(
        f"""
        <div class="callout">
            <div class="callout-title">
                Executive Signal
            </div>
            <div class="callout-text">
                The current filtered portfolio contains
                <b>{num(shortage)}</b> shortage SKUs and
                <b>{num(critical)}</b> critical-risk SKUs.
                Recommended replenishment is
                <b>{num(replenishment)}</b> units.
                Overall WAPE is
                <b>{dec(wape)}%</b>.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    left, right = st.columns(2)

    with left:

        risk_data = (
            filtered["risk_level"]
            .value_counts()
            .reindex(
                ["Critical", "High", "Low"],
                fill_value=0
            )
            .reset_index()
        )

        risk_data.columns = [
            "Risk Level",
            "SKUs"
        ]

        fig = px.bar(
            risk_data,
            x="Risk Level",
            y="SKUs",
            title="Risk Distribution",
            text="SKUs"
        )

        fig.update_traces(
            textposition="outside"
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True
        )

    with right:

        status_data = (
            filtered["inventory_status"]
            .value_counts()
            .reindex(
                ["SHORTAGE", "SURPLUS", "BALANCED"],
                fill_value=0
            )
            .reset_index()
        )

        status_data.columns = [
            "Inventory Status",
            "SKUs"
        ]

        fig = px.bar(
            status_data,
            x="Inventory Status",
            y="SKUs",
            title="Inventory Position",
            text="SKUs"
        )

        fig.update_traces(
            textposition="outside"
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True
        )

    st.markdown("### Highest-Priority SKUs")

    priority_columns = [
        "sku_id",
        "sku_name",
        "category",
        "forecast_demand",
        "stock_on_hand",
        "inventory_gap",
        "inventory_risk_score",
        "risk_level",
        "inventory_status",
        "recommended_action",
        "recommended_replenishment_units"
    ]

    priority_columns = [
        c for c in priority_columns
        if c in filtered.columns
    ]

    priority = (
        filtered[priority_columns]
        .sort_values(
            "inventory_risk_score",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        priority,
        use_container_width=True,
        hide_index=True
    )


# =============================================================================
# SALES & FORECAST
# =============================================================================

elif page == "📈 Sales & Forecast":

    st.markdown("## Sales & Forecast Intelligence")

    st.caption(
        "Compare forecast demand against actual demand and monitor forecast accuracy."
    )

    f = forecast_df.copy()

    if selected_categories and "sku_id" in f.columns:

        category_map = (
            sku_df[
                ["sku_id", "category"]
            ]
            .drop_duplicates("sku_id")
        )

        f = f.merge(
            category_map,
            on="sku_id",
            how="left"
        )

        f = f[
            f["category"]
            .isin(selected_categories)
        ]

    forecast_total = numeric_series(
        f,
        "final_forecast"
    ).sum()

    actual_total = numeric_series(
        f,
        "actual_units"
    ).sum()

    absolute_error = numeric_series(
        f,
        "absolute_error"
    ).sum()

    local_wape = (
        absolute_error / actual_total * 100
        if actual_total > 0
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card(
            "Forecast Units",
            num(forecast_total)
        )

    with c2:
        kpi_card(
            "Actual Units",
            num(actual_total)
        )

    with c3:
        kpi_card(
            "Absolute Error",
            num(absolute_error)
        )

    with c4:
        kpi_card(
            "WAPE",
            f"{local_wape:.2f}%"
        )

    if "week_start" in f.columns:

        weekly = (
            f.groupby("week_start", as_index=False)
            .agg(
                forecast=(
                    "final_forecast",
                    "sum"
                ),
                actual=(
                    "actual_units",
                    "sum"
                )
            )
            .sort_values("week_start")
        )

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=weekly["week_start"],
                y=weekly["forecast"],
                mode="lines",
                name="Forecast"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=weekly["week_start"],
                y=weekly["actual"],
                mode="lines",
                name="Actual"
            )
        )

        fig.update_layout(
            title="Weekly Forecast vs Actual",
            xaxis_title="Week",
            yaxis_title="Units"
        )

        st.plotly_chart(
            style_chart(fig, 430),
            use_container_width=True
        )

    col1, col2 = st.columns(2)

    with col1:

        error_data = f.copy()

        error_data["error"] = (
            numeric_series(
                error_data,
                "final_forecast"
            )
            -
            numeric_series(
                error_data,
                "actual_units"
            )
        )

        fig = px.histogram(
            error_data,
            x="error",
            nbins=40,
            title="Forecast Error Distribution"
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True
        )

    with col2:

        if "sku_id" in f.columns:

            error_by_sku = (
                f.groupby("sku_id", as_index=False)
                ["absolute_error"]
                .sum()
                .sort_values(
                    "absolute_error",
                    ascending=False
                )
                .head(10)
            )

            fig = px.bar(
                error_by_sku,
                x="sku_id",
                y="absolute_error",
                title="Top SKUs by Forecast Error"
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

    st.markdown("### Forecast Detail")

    display_f = f.copy()

    if "week_start" in display_f.columns:
        display_f["week_start"] = (
            display_f["week_start"]
            .dt.strftime("%Y-%m-%d")
        )

    if "week_end" in display_f.columns:
        display_f["week_end"] = (
            display_f["week_end"]
            .dt.strftime("%Y-%m-%d")
        )

    st.dataframe(
        display_f.head(1000),
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download Forecast Data",
        f.to_csv(index=False),
        "forecast_vs_actual_filtered.csv",
        "text/csv"
    )


# =============================================================================
# INVENTORY RISK
# =============================================================================

elif page == "⚠️ Inventory Risk":

    st.markdown("## Inventory Risk Intelligence")

    st.caption(
        "Identify the SKUs requiring the greatest inventory attention."
    )

    risk = filtered.copy()

    critical = int(
        text_series(
            risk,
            "risk_level"
        ).eq("Critical").sum()
    )

    high = int(
        text_series(
            risk,
            "risk_level"
        ).eq("High").sum()
    )

    shortage = int(
        text_series(
            risk,
            "inventory_status"
        ).eq("SHORTAGE").sum()
    )

    avg_score = numeric_series(
        risk,
        "inventory_risk_score"
    ).mean()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card(
            "Critical Risk",
            num(critical)
        )

    with c2:
        kpi_card(
            "High Risk",
            num(high)
        )

    with c3:
        kpi_card(
            "Shortage SKUs",
            num(shortage)
        )

    with c4:
        kpi_card(
            "Average Risk",
            dec(avg_score)
        )

    left, right = st.columns(2)

    with left:

        if "risk_level" in risk.columns:

            risk_distribution = (
                risk["risk_level"]
                .value_counts()
                .reindex(
                    ["Critical", "High", "Low"],
                    fill_value=0
                )
                .reset_index()
            )

            risk_distribution.columns = [
                "Risk Level",
                "SKUs"
            ]

            fig = px.bar(
                risk_distribution,
                x="Risk Level",
                y="SKUs",
                title="Risk Level Distribution",
                text="SKUs"
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

    with right:

        if "category" in risk.columns:

            category_risk = (
                risk.groupby("category", as_index=False)
                ["inventory_risk_score"]
                .mean()
                .sort_values(
                    "inventory_risk_score",
                    ascending=False
                )
            )

            fig = px.bar(
                category_risk,
                x="inventory_risk_score",
                y="category",
                orientation="h",
                title="Average Risk by Category"
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True
            )

    if (
        "forecast_demand" in risk.columns
        and "stock_on_hand" in risk.columns
    ):

        fig = px.scatter(
            risk,
            x="forecast_demand",
            y="stock_on_hand",
            size="inventory_risk_score",
            hover_name="sku_id",
            hover_data=[
                c for c in [
                    "sku_name",
                    "category",
                    "risk_level",
                    "inventory_status"
                ]
                if c in risk.columns
            ],
            title="Demand vs Stock Exposure"
        )

        st.plotly_chart(
            style_chart(fig, 450),
            use_container_width=True
        )

    st.markdown("### Highest-Risk SKUs")

    risk_columns = [
        "sku_id",
        "sku_name",
        "category",
        "forecast_demand",
        "stock_on_hand",
        "inventory_gap",
        "inventory_risk_score",
        "risk_level",
        "inventory_status",
        "recommended_action",
        "sales_value_at_risk"
    ]

    risk_columns = [
        c for c in risk_columns
        if c in risk.columns
    ]

    risk_table = (
        risk[risk_columns]
        .sort_values(
            "inventory_risk_score",
            ascending=False
        )
        .head(100)
    )

    st.dataframe(
        risk_table,
        use_container_width=True,
        hide_index=True
    )


# =============================================================================
# REPLENISHMENT
# =============================================================================

elif page == "📦 Replenishment":

    st.markdown("## Replenishment Intelligence")

    st.caption(
        "Prioritize SKUs where available stock does not cover forecast demand."
    )

    repl = filtered.copy()

    repl["recommended_replenishment_units"] = numeric_series(
        repl,
        "recommended_replenishment_units"
    )

    repl = repl[
        repl["recommended_replenishment_units"] > 0
    ]

    total_units = repl[
        "recommended_replenishment_units"
    ].sum()

    shortage_skus = len(repl)

    critical_repl = int(
        text_series(
            repl,
            "risk_level"
        ).eq("Critical").sum()
    )

    demand_gap = abs(
        numeric_series(
            repl,
            "inventory_gap"
        ).sum()
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card(
            "Shortage SKUs",
            num(shortage_skus)
        )

    with c2:
        kpi_card(
            "Replenishment Units",
            num(total_units)
        )

    with c3:
        kpi_card(
            "Critical Replenishment",
            num(critical_repl)
        )

    with c4:
        kpi_card(
            "Demand Gap",
            num(demand_gap)
        )

    if "category" in repl.columns:

        category_repl = (
            repl.groupby("category", as_index=False)
            ["recommended_replenishment_units"]
            .sum()
            .sort_values(
                "recommended_replenishment_units",
                ascending=False
            )
        )

        fig = px.bar(
            category_repl,
            x="category",
            y="recommended_replenishment_units",
            title="Replenishment Requirement by Category"
        )

        fig.update_xaxes(
            tickangle=-40
        )

        st.plotly_chart(
            style_chart(fig, 430),
            use_container_width=True
        )

    st.markdown("### Replenishment Priority Queue")

    repl_columns = [
        "sku_id",
        "sku_name",
        "category",
        "forecast_demand",
        "stock_on_hand",
        "inventory_gap",
        "inventory_risk_score",
        "risk_level",
        "recommended_action",
        "recommended_replenishment_units",
        "sales_value_at_risk"
    ]

    repl_columns = [
        c for c in repl_columns
        if c in repl.columns
    ]

    queue = (
        repl[repl_columns]
        .sort_values(
            [
                "inventory_risk_score",
                "recommended_replenishment_units"
            ],
            ascending=[False, False]
        )
        .head(100)
    )

    st.dataframe(
        queue,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download Replenishment Priority",
        repl.to_csv(index=False),
        "replenishment_priority.csv",
        "text/csv"
    )


# =============================================================================
# OVERSTOCK
# =============================================================================

elif page == "🏷️ Overstock / Markdown":

    st.markdown("## Overstock & Markdown Intelligence")

    st.caption(
        "Identify surplus stock and quantify capital tied up in excess inventory."
    )

    over = filtered.copy()

    over["excess_inventory_units"] = numeric_series(
        over,
        "excess_inventory_units"
    )

    over = over[
        over["excess_inventory_units"] > 0
    ]

    excess_units = over[
        "excess_inventory_units"
    ].sum()

    capital = numeric_series(
        over,
        "capital_locked_in_overstock"
    ).sum()

    surplus_skus = len(over)

    avg_excess = (
        over["excess_inventory_units"].mean()
        if len(over) > 0
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card(
            "Surplus SKUs",
            num(surplus_skus)
        )

    with c2:
        kpi_card(
            "Excess Units",
            num(excess_units)
        )

    with c3:
        kpi_card(
            "Capital Locked",
            money(capital)
        )

    with c4:
        kpi_card(
            "Avg Excess / SKU",
            num(avg_excess)
        )

    if "category" in over.columns:

        category_over = (
            over.groupby("category", as_index=False)
            ["capital_locked_in_overstock"]
            .sum()
            .sort_values(
                "capital_locked_in_overstock",
                ascending=False
            )
        )

        fig = px.bar(
            category_over,
            x="category",
            y="capital_locked_in_overstock",
            title="Capital Locked by Category"
        )

        fig.update_xaxes(
            tickangle=-40
        )

        st.plotly_chart(
            style_chart(fig, 430),
            use_container_width=True
        )

    st.markdown("### Highest-Exposure Surplus SKUs")

    over_columns = [
        "sku_id",
        "sku_name",
        "category",
        "forecast_demand",
        "stock_on_hand",
        "inventory_gap",
        "excess_inventory_units",
        "inventory_risk_score",
        "recommended_action",
        "capital_locked_in_overstock"
    ]

    over_columns = [
        c for c in over_columns
        if c in over.columns
    ]

    over_table = (
        over[over_columns]
        .sort_values(
            "capital_locked_in_overstock",
            ascending=False
        )
        .head(100)
    )

    st.dataframe(
        over_table,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download Overstock Analysis",
        over.to_csv(index=False),
        "overstock_analysis.csv",
        "text/csv"
    )


# =============================================================================
# SKU EXPLORER
# =============================================================================

elif page == "🔎 SKU Explorer":

    st.markdown("## SKU Explorer")

    st.caption(
        "Search and inspect individual SKUs."
    )

    search = st.text_input(
        "Search SKU or product name",
        placeholder="Example: SKU00002 or CrispKing"
    )

    explorer = filtered.copy()

    if search.strip():

        term = search.strip().lower()

        id_match = (
            explorer["sku_id"]
            .astype(str)
            .str.lower()
            .str.contains(
                term,
                na=False
            )
        )

        name_match = (
            explorer["sku_name"]
            .astype(str)
            .str.lower()
            .str.contains(
                term,
                na=False
            )
        )

        explorer = explorer[
            id_match | name_match
        ]

    st.write(
        f"Matching SKUs: **{len(explorer):,}**"
    )

    if len(explorer) == 0:

        st.warning(
            "No SKU matched the current filters."
        )

    else:

        selected_sku = st.selectbox(
            "Select SKU",
            explorer["sku_id"]
            .astype(str)
            .tolist()
        )

        row = explorer[
            explorer["sku_id"]
            .astype(str)
            == selected_sku
        ].iloc[0]

        st.markdown(
            f"### {row['sku_name']}"
        )

        st.caption(
            f"{row['sku_id']} • {row['category']}"
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            kpi_card(
                "Forecast Demand",
                num(row["forecast_demand"])
            )

        with c2:
            kpi_card(
                "Actual Units",
                num(row["actual_units"])
            )

        with c3:
            kpi_card(
                "Stock on Hand",
                num(row["stock_on_hand"])
            )

        with c4:
            kpi_card(
                "Risk Score",
                dec(row["inventory_risk_score"])
            )

        c5, c6, c7 = st.columns(3)

        with c5:
            kpi_card(
                "Inventory Gap",
                num(row["inventory_gap"])
            )

        with c6:
            kpi_card(
                "Inventory Status",
                str(row["inventory_status"])
            )

        with c7:
            kpi_card(
                "Recommended Action",
                str(row["recommended_action"])
            )

        c8, c9 = st.columns(2)

        with c8:
            kpi_card(
                "Sales Value at Risk",
                money(row["sales_value_at_risk"])
            )

        with c9:
            kpi_card(
                "Capital Locked",
                money(row["capital_locked_in_overstock"])
            )

        st.markdown("### Complete SKU Record")

        st.dataframe(
            pd.DataFrame([row]),
            use_container_width=True,
            hide_index=True
        )


# =============================================================================
# CATEGORY INTELLIGENCE
# =============================================================================

elif page == "📊 Category Intelligence":

    st.markdown("## Category Intelligence")

    st.caption(
        "Compare demand, inventory risk, shortage exposure and financial impact by category."
    )

    cat = category_df.copy()

    if selected_categories and "category" in cat.columns:

        cat = cat[
            cat["category"]
            .isin(selected_categories)
        ]

    total_categories = len(cat)

    forecast_total = numeric_series(
        cat,
        "forecast_demand"
    ).sum()

    actual_total = numeric_series(
        cat,
        "actual_units"
    ).sum()

    replenishment_total = numeric_series(
        cat,
        "replenishment_units"
    ).sum()

    capital_total = numeric_series(
        cat,
        "capital_locked_in_overstock"
    ).sum()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card(
            "Categories",
            num(total_categories)
        )

    with c2:
        kpi_card(
            "Forecast Demand",
            num(forecast_total)
        )

    with c3:
        kpi_card(
            "Actual Units",
            num(actual_total)
        )

    with c4:
        kpi_card(
            "Replenishment",
            num(replenishment_total)
        )

    left, right = st.columns(2)

    with left:

        if "average_inventory_risk" in cat.columns:

            risk_cat = (
                cat.sort_values(
                    "average_inventory_risk",
                    ascending=False
                )
            )

            fig = px.bar(
                risk_cat,
                x="category",
                y="average_inventory_risk",
                title="Average Inventory Risk"
            )

            fig.update_xaxes(
                tickangle=-40
            )

            st.plotly_chart(
                style_chart(fig, 430),
                use_container_width=True
            )

    with right:

        if "replenishment_units" in cat.columns:

            repl_cat = (
                cat.sort_values(
                    "replenishment_units",
                    ascending=False
                )
            )

            fig = px.bar(
                repl_cat,
                x="category",
                y="replenishment_units",
                title="Replenishment Units"
            )

            fig.update_xaxes(
                tickangle=-40
            )

            st.plotly_chart(
                style_chart(fig, 430),
                use_container_width=True
            )

    if "sales_value_at_risk" in cat.columns:

        fig = px.bar(
            cat.sort_values(
                "sales_value_at_risk",
                ascending=False
            ),
            x="category",
            y="sales_value_at_risk",
            title="Sales Value at Risk by Category"
        )

        fig.update_xaxes(
            tickangle=-40
        )

        st.plotly_chart(
            style_chart(fig, 430),
            use_container_width=True
        )

    st.markdown("### Category Performance")

    st.dataframe(
        cat.sort_values(
            "average_inventory_risk",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download Category Intelligence",
        cat.to_csv(index=False),
        "category_intelligence.csv",
        "text/csv"
    )


# =============================================================================
# FOOTER
# =============================================================================

st.markdown(
    """
    <br>
    <div style="
        border-top:1px solid #252c36;
        padding-top:16px;
        color:#64748b;
        font-size:11px;
        text-align:center;
    ">
        PROJECT FORESIGHT
        • Demand Forecasting
        • Inventory Risk
        • Business Intelligence
        <br>
        Built from validated Project Foresight dashboard datasets
    </div>
    """,
    unsafe_allow_html=True
)
