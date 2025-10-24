#!/usr/bin/env python3
"""
Streamlit app to visualize department salary summaries (average, min, max).

Usage:
    pip install -r requirements.txt
    streamlit run app.py

Deploy:
    Push this repo to GitHub and create a new app on Streamlit Cloud that points to app.py.
"""
from io import BytesIO
import base64

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Salary Visualizer", layout="wide")

EXAMPLE_CSV = """Department,Average_Salary,Min_Salary,Max_Salary
IT,28560.182889,10544.19,115178.51
Finance,28055.533689,8987.86,101294.41
Logistics/Warehousing,27574.698600,9027.53,153451.58
Store Operations,27404.359873,8848.62,177873.61
Fresh Produce,26915.946969,8998.42,110475.60
Marketing,26796.816800,9736.23,65923.63
HR,26539.921733,8823.46,58951.29
Meat/Fish & Bakery,26535.722133,8867.88,116453.67
Customer Service,26244.393800,9449.99,50949.01
"""

def load_data(uploaded_file):
    if uploaded_file is None:
        df = pd.read_csv(BytesIO(EXAMPLE_CSV.encode("utf-8")));
    else:
        df = pd.read_csv(uploaded_file);
    df.columns = [c.strip() for c in df.columns];
    for c in ["Average_Salary", "Min_Salary", "Max_Salary"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce");
    return df;

def make_bar_fig(df, palette="Plotly", show_error=True, title="Average Salary by Department"):
    y = df["Department"].tolist();
    x = df["Average_Salary"].tolist();
    left_err = (df["Average_Salary"] - df["Min_Salary"]).fillna(0).tolist();
    right_err = (df["Max_Salary"] - df["Average_Salary"]).fillna(0).tolist();

    fig = go.Figure();
    fig.add_trace(
        go.Bar(
            x=x,
            y=y,
            orientation="h",
            marker=dict(color=px.colors.qualitative.Plotly if palette == "Plotly" else None),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Average: $%{x:,.2f}<br>"
                "Min: $%{customdata[0]:,.2f}<br>"
                "Max: $%{customdata[1]:,.2f}<extra></extra>"
            ),
            customdata=np.stack([df["Min_Salary"].fillna(0), df["Max_Salary"].fillna(0)], axis=1),
        )
    )

    if show_error:
        fig.data[0].update(
            error_x=dict(
                type="data",
                symmetric=False,
                array=right_err,
                arrayminus=left_err,
                thickness=1.5,
                width=6,
                color="rgba(0,0,0,0.7)",
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title="Salary (USD)",
        yaxis=dict(autorange="reversed"),
        margin=dict(l=220, r=40, t=80, b=40),
        template="plotly_white",
        height=60 * max(4, len(df)),
    )
    fig.update_xaxes(tickformat=",")
    return fig;

def simulate_distributions(df, samples_per_dept=300, seed=42):
    rng = np.random.default_rng(seed);
    rows = [];
    for _, r in df.iterrows():
        try:
            a, b, c = float(r["Min_Salary"]), float(r["Average_Salary"]), float(r["Max_Salary"]);
        except Exception:
            continue;
        if np.isnan(a) or np.isnan(b) or np.isnan(c) or a >= c:
            continue;
        samples = rng.triangular(a, b, c, size=samples_per_dept);
        dept = r["Department"];
        rows.append(pd.DataFrame({"Department": dept, "Salary": samples}));
    if not rows:
        return pd.DataFrame(columns=["Department", "Salary"]);
    return pd.concat(rows, ignore_index=True);

def fig_to_png_bytes(fig):
    return fig.to_image(format="png", scale=2);

st.title("Salary Summary Visualizer (Average, Min, Max)");

with st.sidebar:
    st.header("Data");
    uploaded = st.file_uploader("Upload CSV (columns: Department, Average_Salary, Min_Salary, Max_Salary)", type=["csv"]);
    df = load_data(uploaded);

    st.markdown("Preview of loaded data:");
    st.dataframe(df.head(50));

    st.markdown("---");
    st.header("Chart options");
    sort_choice = st.radio("Sort by", options=["Average (desc)", "Average (asc)", "Department (A-Z)"]);
    show_error = st.checkbox("Show Min/Max ranges as error bars", value=True);
    palette = st.selectbox("Color palette", options=["Plotly", "Blues", "Viridis", "Mako"], index=0);

    st.markdown("---");
    st.header("Filter");
    all_departments = df["Department"].dropna().astype(str).tolist() if "Department" in df.columns else [];
    selected = st.multiselect("Select departments (empty = all)", options=all_departments, default=all_departments);

    st.markdown("---");
    st.header("Simulated distributions (optional)");
    show_sim = st.checkbox("Show simulated violin plots (triangular from Min/Average/Max)", value=False);
    sim_samples = st.slider("Samples per department (simulation)", min_value=50, max_value=2000, value=300, step=50);
    st.markdown("Simulation warning: only use for illustration when you don't have raw salary records. Simulated data is not the real distribution.");

required_cols = {"Department", "Average_Salary", "Min_Salary", "Max_Salary"};
if not required_cols.issubset(set(df.columns)):
    st.error(f"CSV must contain columns: {', '.join(sorted(required_cols))}.");
    st.stop();

df = df.dropna(subset=["Department"]).copy();
df["Department"] = df["Department"].astype(str);

if selected:
    df = df[df["Department"].isin(selected)];

if sort_choice == "Average (desc)":
    df_sorted = df.sort_values("Average_Salary", ascending=False).reset_index(drop=True);
elif sort_choice == "Average (asc)":
    df_sorted = df.sort_values("Average_Salary", ascending=True).reset_index(drop=True);
else:
    df_sorted = df.sort_values("Department", ascending=True).reset_index(drop=True);

col1, col2 = st.columns([2, 1]);

with col1:
    st.subheader("Average Salary with Min/Max Ranges");
    bar_fig = make_bar_fig(df_sorted, palette=palette, show_error=show_error);
    st.plotly_chart(bar_fig, use_container_width=True);

    try:
        png_bytes = fig_to_png_bytes(bar_fig);
        st.download_button(
            label="Download chart as PNG",
            data=png_bytes,
            file_name="average_salary_chart.png",
            mime="image/png",
        );
    except Exception:
        st.info("PNG export requires the 'kaleido' package. Install with: pip install -U kaleido");

    html = bar_fig.to_html(include_plotlyjs="cdn");
    st.download_button(
        label="Download interactive chart (HTML)",
        data=html.encode("utf-8"),
        file_name="average_salary_chart.html",
        mime="text/html",
    );

    st.markdown("### Table (current view)");
    st.dataframe(df_sorted.style.format({"Average_Salary": "${:,.2f}", "Min_Salary": "${:,.2f}", "Max_Salary": "${:,.2f}"}));

with col2:
    st.subheader("Summary statistics");
    avg_of_avgs = df_sorted["Average_Salary"].mean();
    st.metric("Mean of department averages", f"${avg_of_avgs:,.2f}", help="Average of the Average_Salary column");
    st.write("Departments shown:", len(df_sorted));
    st.write("Min of mins:", f"${df_sorted['Min_Salary'].min():,.2f}");
    st.write("Max of maxes:", f"${df_sorted['Max_Salary'].max():,.2f}");

    st.markdown("---");
    if show_sim:
        st.subheader("Simulated distributions (illustrative)");
        sim_df = simulate_distributions(df_sorted, samples_per_dept=sim_samples);
        if sim_df.empty:
            st.warning("Not enough valid Min/Average/Max ranges to simulate distributions.");
        else:
            violin_fig = px.violin(sim_df, x="Salary", y="Department", orientation="h", points="none", color="Department", box=True);
            violin_fig.update_layout(margin=dict(l=220, r=40, t=40, b=40), height=60 * max(4, len(df_sorted)));
            violin_fig.update_xaxes(tickformat=",");
            st.plotly_chart(violin_fig, use_container_width=True);

            sim_html = violin_fig.to_html(include_plotlyjs="cdn");
            st.download_button(
                label="Download simulated violin (HTML)",
                data=sim_html.encode("utf-8"),
                file_name="simulated_violin.html",
                mime="text/html",
            );

st.markdown(
    """
Notes:
- The bar chart shows the department Average_Salary with Min/Max ranges shown as asymmetric error bars.
- If you want boxplots or real distribution plots, provide raw salary records instead of min/avg/max summaries.
- Simulated violin plots use a triangular distribution (min, mode=average, max) and are for illustration only.
"""
)
