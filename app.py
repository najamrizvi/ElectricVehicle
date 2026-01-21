import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="EV Analytics Dashboard",
    page_icon="⚡",
    layout="wide"
)

# --------------------------------------------------
# BACKGROUND & STYLES
# --------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0b1d2d, #1c3b57, #102a43);
}

.title {
    font-size: 46px;
    font-weight: 800;
    color: #00e5ff;
    text-align: center;
}

.subtitle {
    font-size: 20px;
    color: #ffffff;
    text-align: center;
    margin-bottom: 25px;
}

.kpi {
    background-color: #162e45;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
}

.kpi-value {
    font-size: 32px;
    font-weight: bold;
    color: #00e676;
}

.kpi-label {
    color: white;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# LOAD DATA (AUTO-DETECT CSV — ERROR PROOF)
# --------------------------------------------------
@st.cache_data
def load_data():
    files = [f for f in os.listdir() if f.lower().endswith(".csv")]

    if len(files) == 0:
        st.error("❌ No CSV file found in the folder.")
        st.stop()

    if len(files) > 1:
        st.error("❌ Multiple CSV files found. Keep only ONE CSV in the folder.")
        st.write(files)
        st.stop()

    df = pd.read_csv(files[0])
    return df

df = load_data()

# --------------------------------------------------
# DATA CLEANING
# --------------------------------------------------
df["model_year"] = df["model_year"].astype(int)
df["electric_range"] = df["electric_range"].fillna(0).astype(int)
df["base_msrp"] = df["base_msrp"].fillna(0).astype(int)

df["longitude"] = df["vehicle_location"].str.extract(r"POINT \(([-\d\.]+)")
df["latitude"] = df["vehicle_location"].str.extract(r"([-\d\.]+)\)$")

df["latitude"] = df["latitude"].astype(float)
df["longitude"] = df["longitude"].astype(float)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown('<div class="title">⚡ Electric Vehicle Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Clean • Fast • Error-Free • Professional</div>', unsafe_allow_html=True)

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.header("🔎 Filters")

year = st.sidebar.multiselect(
    "Model Year",
    sorted(df["model_year"].unique()),
    default=sorted(df["model_year"].unique())
)

make = st.sidebar.multiselect(
    "Manufacturer",
    sorted(df["make"].unique()),
    default=sorted(df["make"].unique())
)

df_f = df[
    (df["model_year"].isin(year)) &
    (df["make"].isin(make))
]

# --------------------------------------------------
# KPI METRICS
# --------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

c1.markdown(f"""
<div class="kpi">
<div class="kpi-value">{len(df_f)}</div>
<div class="kpi-label">Total EVs</div>
</div>
""", unsafe_allow_html=True)

c2.markdown(f"""
<div class="kpi">
<div class="kpi-value">{df_f['make'].nunique()}</div>
<div class="kpi-label">Manufacturers</div>
</div>
""", unsafe_allow_html=True)

c3.markdown(f"""
<div class="kpi">
<div class="kpi-value">{int(df_f['electric_range'].mean())}</div>
<div class="kpi-label">Avg Mileage</div>
</div>
""", unsafe_allow_html=True)

c4.markdown(f"""
<div class="kpi">
<div class="kpi-value">{df_f['city'].nunique()}</div>
<div class="kpi-label">Cities</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --------------------------------------------------
# CHARTS
# --------------------------------------------------
fig_make = px.bar(
    df_f.groupby("make").size().reset_index(name="Count"),
    x="make", y="Count",
    title="EV Count by Manufacturer"
)
st.plotly_chart(fig_make, use_container_width=True)

fig_year = px.line(
    df_f.groupby("model_year").size().reset_index(name="Count"),
    x="model_year", y="Count",
    markers=True,
    title="EV Growth Over Years"
)
st.plotly_chart(fig_year, use_container_width=True)

# --------------------------------------------------
# CORRELATION
# --------------------------------------------------
fig_corr = px.imshow(
    df_f[["model_year", "electric_range", "base_msrp"]].corr(),
    text_auto=True,
    title="Correlation Heatmap"
)
st.plotly_chart(fig_corr, use_container_width=True)

# --------------------------------------------------
# MAP (ZERO DELAY)
# --------------------------------------------------
fig_map = px.scatter_mapbox(
    df_f,
    lat="latitude",
    lon="longitude",
    color="make",
    zoom=6,
    height=550,
    title="EV Geographic Distribution",
    hover_data=["city", "model", "electric_range"]
)
fig_map.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig_map, use_container_width=True)
