import streamlit as st
import pandas as pd
import os

# ------------------- CONFIG -------------------
EXCEL_PATH = "Sample.xlsx"
st.set_page_config(page_title="NOC Dashboard Spread-3", layout="wide")

# ------------------- SESSION STATE INIT -------------------
for key in ["selected_type", "selected_district", "selected_status", 
            "show_received", "show_not_received"]:
    if key not in st.session_state:
        st.session_state[key] = None if "show" not in key else False

# ------------------- LOAD DATA -------------------
@st.cache_data(ttl=60)
def load_data(path):
    return pd.read_excel(path)

df = load_data(EXCEL_PATH)

df.columns = df.columns.str.strip()  # Remove leading/trailing spaces

# ------------------- UI: TYPE OF CROSSING -------------------
st.title("📊 NOC Dashboard")
st.subheader("Click a Crossing Type to explore details")

type_counts = df['Type of Crossing'].value_counts().to_dict()
type_cols = st.columns(len(type_counts))

for i, (t, count) in enumerate(type_counts.items()):
    if type_cols[i].button(f"🔘 {t} ({count})", key=f"type_{t}"):
        st.session_state.selected_type = t
        st.session_state.selected_district = None
        st.session_state.selected_status = None
        st.session_state.show_received = False
        st.session_state.show_not_received = False

# ------------------- UI: DISTRICTS -------------------
if st.session_state.selected_type:
    st.markdown(f"### 🛤️ Districts in **{st.session_state.selected_type}**")
    filtered_df = df[df['Type of Crossing'] == st.session_state.selected_type]
    district_counts = filtered_df['District'].value_counts().to_dict()
    district_cols = st.columns(len(district_counts))

    for i, (district, count) in enumerate(district_counts.items()):
        if district_cols[i].button(f"🏙️ {district} ({count})", key=f"district_{district}"):
            st.session_state.selected_district = district
            st.session_state.selected_status = None
            st.session_state.show_received = False
            st.session_state.show_not_received = False

# ------------------- UI: NOC STATUS -------------------
if st.session_state.selected_district:
    dist_df = filtered_df[filtered_df['District'] == st.session_state.selected_district]
    received_count = (dist_df['NOC Status'].str.lower() == 'received').sum()
    not_received_count = (dist_df['NOC Status'].str.lower() != 'received').sum()

    st.markdown(f"### 📄 NOC Status in **{st.session_state.selected_district}**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button(f"🟢 Received ({received_count})", key="received_btn"):
            st.session_state.show_received = not st.session_state.show_received
            st.session_state.show_not_received = False

    with col2:
        if st.button(f"🔴 Not Received ({not_received_count})", key="not_received_btn"):
            st.session_state.show_not_received = not st.session_state.show_not_received
            st.session_state.show_received = False

    # ----------- Show Received Table -----------
    if st.session_state.show_received:
        received_df = dist_df[dist_df['NOC Status'].str.lower() == 'received']
        st.markdown("#### ✅ NOCs Received")
        st.dataframe(received_df.reset_index(drop=True), use_container_width=True)

    # ----------- Show Not Received Table + Update Option -----------
    if st.session_state.show_not_received:
        not_received_df = dist_df[dist_df['NOC Status'].str.lower() != 'received'].copy()
        st.markdown("#### ❌ NOCs Not Received")

        for i, row in not_received_df.iterrows():
            col1, col2 = st.columns([6, 2])
            with col1:
                st.write(f"📍 **{row['Area']}**")
            with col2:
                if st.button("Mark as Received", key=f"mark_{i}"):
                    df.loc[(df['Type of Crossing'] == st.session_state.selected_type) &
                           (df['District'] == st.session_state.selected_district) &
                           (df['Area'] == row['Area']), 'NOC Status'] = "Received"
                    df.to_excel(EXCEL_PATH, index=False)
                    st.success(f"Marked '{row['Area']}' as Received")
                    st.rerun()
