"""
Olist delivery dashboard — starter app.

Run from the repo root:
    streamlit run app/app.py

Fill in the captions marked [FILL IN] once you've seen your actual numbers,
and add the 'worst offenders' and recommendations sections in Week 3.
"""
import sys
from pathlib import Path

import streamlit as st
import plotly.express as px

# Make `src` importable when run from the repo root
sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.data_loader import (  # noqa: E402
    get_connection,
    get_kpis,
    get_review_vs_late,
    get_late_by_category,
)

st.set_page_config(page_title="Olist Delivery Analysis", layout="wide")


@st.cache_resource
def load():
    return get_connection()


try:
    con = load()
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()

# ── Header ────────────────────────────────────────────────────────────────
st.title("📦 Late Deliveries vs. Reviews — Olist")
st.caption(
    "Where late deliveries are hurting review scores, and which categories "
    "to fix first."
)

kpis = get_kpis(con)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Delivered orders", f"{kpis['total_delivered']:,}")
c2.metric("On-time %", f"{kpis['on_time_pct']}%")
c3.metric("Avg days to deliver", kpis["avg_days_to_deliver"])
c4.metric("Avg review score", kpis["avg_review_score"])

st.divider()

# ── Finding 1: late deliveries vs review score ────────────────────────────
st.subheader("Do late deliveries get worse reviews?")
rev = get_review_vs_late(con)
fig = px.bar(
    rev,
    x="delivery_status",
    y="avg_review_score",
    color="delivery_status",
    text="avg_review_score",
    labels={"delivery_status": "", "avg_review_score": "Avg review score"},
)
fig.update_traces(textposition="outside")
fig.update_layout(showlegend=False, yaxis_range=[0, 5])
st.plotly_chart(fig, use_container_width=True)
st.caption("👉 Takeaway: [FILL IN — e.g. 'Late orders score ~1.3 stars lower.']")

st.divider()

# ── Finding 2: worst categories ───────────────────────────────────────────
st.subheader("Which categories are the worst offenders?")
min_orders = st.slider("Minimum orders per category", 50, 500, 100, step=50)
cat = get_late_by_category(con, min_orders)

fig2 = px.bar(
    cat.head(15).sort_values("late_pct"),
    x="late_pct",
    y="category",
    orientation="h",
    labels={"late_pct": "Late delivery %", "category": ""},
)
st.plotly_chart(fig2, use_container_width=True)
st.caption("👉 Takeaway: [FILL IN — name the top 2–3 categories to prioritise.]")

with st.expander("See the full table"):
    st.dataframe(cat, use_container_width=True)

# ── TODO (Week 3) ─────────────────────────────────────────────────────────
# - Add a 'revenue at risk' metric (join order_items.price to late orders)
# - Add sidebar filters (state, date range)
# - Add a Recommendations section with 3 quantified actions
