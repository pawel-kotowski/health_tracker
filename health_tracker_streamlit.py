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

# Add at the start of the file, after imports
if "show_validation_error" not in st.session_state:
    st.session_state.show_validation_error = False
if "clear_form" not in st.session_state:
    st.session_state.clear_form = False

# When we need to clear the form, set this flag
if st.session_state.clear_form:
    st.session_state.clear_form = False
    st.session_state.new_metric_input = ""
    st.rerun()


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
    # Clear the cache to force reload of data
    load_data.clear()


# Load the existing data
df = load_data()

# Get unique metrics
existing_metrics = sorted(df["Metric"].unique().tolist()) if not df.empty else []


def reset_app_state():
    """Reset all session state variables"""
    st.session_state.clear_form = False
    st.session_state.show_validation_error = False
    st.session_state.confirm_clear = False
    if "new_metric_input" in st.session_state:
        del st.session_state.new_metric_input


# Data management section
with st.expander("Data Management", expanded=True):
    col1, col2, col3 = st.columns(3)

    # Download data
    with col1:
        if not df.empty:
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Metrics Data",
                data=csv,
                file_name="health_metrics.csv",
                mime="text/csv",
            )
        else:
            st.info("No data to download")

    # Upload data
    with col2:
        with st.form("upload_form"):
            uploaded_file = st.file_uploader("Upload Metrics Data", type="csv")
            upload_submitted = st.form_submit_button("Upload")
            
            if upload_submitted and uploaded_file is not None:
                try:
                    uploaded_df = pd.read_csv(uploaded_file)
                    required_columns = ["Date", "Metric", "Value"]

                    if all(col in uploaded_df.columns for col in required_columns):
                        uploaded_df["Date"] = pd.to_datetime(uploaded_df["Date"])
                        save_data(uploaded_df)
                        # Reload data and update metrics list
                        df = load_data()
                        existing_metrics = sorted(df["Metric"].unique().tolist()) if not df.empty else []
                        st.success("Data uploaded successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid file format. Required columns: Date, Metric, Value")
                except Exception as e:
                    st.error(f"Error uploading file: {str(e)}")

    # Clear data
    with col3:
        if "confirm_clear" not in st.session_state:
            st.session_state.confirm_clear = False

        if not st.session_state.confirm_clear:
            if st.button("Clear All Data", type="secondary"):
                st.session_state.confirm_clear = True
                st.rerun()
        else:
            st.warning("⚠️ Are you sure? This will delete all your data!")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes, Clear Everything", type="primary"):
                    df = pd.DataFrame(columns=["Date", "Metric", "Value"])
                    save_data(df)
                    reset_app_state()
                    st.success("All data cleared!")
                    st.rerun()
            with col2:
                if st.button("No, Cancel"):
                    reset_app_state()
                    st.rerun()

# Input form for values
with st.form("entry_form"):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if existing_metrics:
            metric = st.selectbox("Select Metric", ["Select..."] + existing_metrics)
        else:
            metric = "Select..."
            st.info("No metrics yet")

    with col2:
        new_metric = st.text_input(
            "Or Add New Metric",
            key="new_metric_input",
        )
        if new_metric and new_metric in existing_metrics:
            st.error("This metric already exists!")

    with col3:
        value = st.number_input("Value", value=0.0)

    with col4:
        date = st.date_input("Date", value=datetime.now())

    submitted = st.form_submit_button("Add Entry")

    if submitted:
        if new_metric:  # Adding new metric
            if new_metric in existing_metrics:
                st.error(
                    "This metric already exists! Please use the dropdown to select it."
                )
            else:
                try:
                    new_entry = pd.DataFrame(
                        {
                            "Date": [pd.to_datetime(date)],
                            "Metric": [new_metric],
                            "Value": [value],
                        }
                    )
                    df = pd.concat([df, new_entry], ignore_index=True)
                    save_data(df)
                    st.session_state.clear_form = True
                    st.success(f"Added new metric: {new_metric}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding entry: {str(e)}")
        elif metric == "Select...":  # No metric selected
            st.error("Please select a metric or add a new one")
        else:  # Using existing metric
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
                st.rerun()
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
