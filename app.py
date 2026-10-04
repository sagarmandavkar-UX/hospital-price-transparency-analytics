"""Interactive hospital price-transparency exploration dashboard."""

import pandas as pd
import plotly.express as px
import streamlit as st

from analysis import analyze_variation, bootstrap_rural_difference, clean_rates, hospital_outliers, make_demo_rates, payer_price_index


st.set_page_config(page_title="Hospital Price Observatory", page_icon="🏥", layout="wide", initial_sidebar_state="collapsed")
st.title("Hospital Price Observatory")
st.caption("Negotiated-rate variation, payer comparisons, and data-quality diagnostics · seeded demonstration data")

uploaded = st.sidebar.file_uploader("Upload hospital rates", type="csv")
raw = pd.read_csv(uploaded) if uploaded else make_demo_rates()
clean, quality = clean_rates(raw)

procedure_options = sorted(clean["procedure_code"].astype(str).unique())
selected = st.sidebar.multiselect("Procedure codes", procedure_options, default=procedure_options)
filtered = clean.loc[clean["procedure_code"].astype(str).isin(selected)]
summary, drivers = analyze_variation(filtered)
rural = bootstrap_rural_difference(filtered)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Clean rates", f"{quality['clean_rows']:,}", help=f"{quality['input_rows'] - quality['clean_rows']} invalid or duplicate rows excluded")
c2.metric("Hospitals", filtered["hospital"].nunique())
c3.metric("Median price spread", f"{summary['max_to_min_ratio'].median():.2f}×")
c4.metric("Rural median difference", f"{rural['median_difference_pct']:.1f}%", help=f"Bootstrap 95% CI: {rural['ci_low']:.1f}% to {rural['ci_high']:.1f}%")

left, right = st.columns(2)
with left:
    st.subheader("Rate distribution by procedure")
    fig = px.box(filtered, x="procedure_code", y="rate", color="rural", points="outliers", labels={"rate": "Negotiated rate ($)", "procedure_code": "Procedure", "rural": "Rural"})
    st.plotly_chart(fig, width="stretch")
with right:
    st.subheader("Normalized payer price index")
    payer = payer_price_index(filtered)
    fig = px.bar(payer, x="payer", y="median_price_index", text_auto=".2f", color="median_price_index", color_continuous_scale="Blues", labels={"median_price_index": "Median index (1.0 = procedure median)"})
    fig.add_hline(y=1, line_dash="dash")
    st.plotly_chart(fig, width="stretch")

st.subheader("High-price review queue")
threshold = st.slider("Relative-to-benchmark threshold", 1.1, 3.0, 1.5, 0.1)
outliers = hospital_outliers(filtered, threshold)
st.dataframe(outliers[["hospital", "procedure_code", "payer", "rate", "benchmark_rate", "relative_to_benchmark", "rural", "beds"]], width="stretch", hide_index=True)

with st.expander("Data quality and model notes", expanded=True):
    st.write({"quality": quality, "adjusted_model": drivers})
    st.info("Rates are negotiated-price observations, not utilization-weighted patient spending. The adjusted model describes associations and is not causal.")

st.download_button("Download filtered clean rates", filtered.to_csv(index=False), "clean_hospital_rates.csv", "text/csv")
