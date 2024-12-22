import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# Page config
st.set_page_config(page_title="Health Metrics Tracker", layout="wide")
st.title("Health Metrics Tracker")

# Initialize data storage
DATA_FILE = "health_metrics.csv"


# Load data
@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df["Date"] = pd.to_datetime(df["Date"])
        return df
    return pd.DataFrame(columns=["Date", "Metric", "Value"])


def save_data(df):
    df.to_csv(DATA_FILE, index=False)


# Load the existing data
df = load_data()

# Get unique metrics and add an "Add New Metric" option
existing_metrics = sorted(df["Metric"].unique().tolist()) if not df.empty else []
metric_options = existing_metrics + ["Add New Metric"]

# Input form
with st.form("entry_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        metric_choice = st.selectbox(
            "Select Metric", metric_options, index=0 if existing_metrics else None
        )
        if metric_choice == "Add New Metric":
            metric = st.text_input("Enter New Metric")
        else:
            metric = metric_choice

    with col2:
        value = st.number_input("Value", value=0.0)

    with col3:
        date = st.date_input("Date", value=datetime.now())

    submitted = st.form_submit_button("Add Entry")

    if submitted:
        if metric_choice == "Add New Metric" and not metric:
            st.error("Please enter a new metric name")
        else:
            try:
                new_entry = pd.DataFrame(
                    {
                        "Date": [pd.to_datetime(date)],
                        "Metric": [metric],
                        "Value": [value],
                    }
                )

                df = pd.concat([df, new_entry], ignore_index=True)
                save_data(df)
                st.success("Entry added successfully!")

            except Exception as e:
                st.error(f"Error adding entry: {str(e)}")

# Display graph
if not df.empty:
    # No need to filter for specific metric anymore
    plot_data = df.copy()
    plot_data = plot_data.sort_values("Date")

    fig = px.line(
        plot_data,
        x="Date",
        y="Value",
        color="Metric",
        title="All Metrics Over Time",
        markers=True,
        color_discrete_sequence=[
            "#1f77b4",  # blue
            "#ff7f0e",  # orange
            "#2ca02c",  # green
            "#d62728",  # red
            "#9467bd",  # purple
            "#8c564b",  # brown
            "#e377c2",  # pink
            "#7f7f7f",  # gray
            "#bcbd22",  # olive
            "#17becf",  # cyan
        ],
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Value",
        hovermode="x unified",
        legend_title="Metrics",
    )

    st.plotly_chart(fig, use_container_width=True)

# Display data table
if not df.empty:
    st.subheader("Data Table")
    display_df = df.copy()
    display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")
    st.dataframe(
        display_df.sort_values("Date", ascending=False),
        use_container_width=True,
        hide_index=True,
    )
