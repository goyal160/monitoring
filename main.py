import streamlit as st
from db_utils import load_data, update_noc_status, get_data_by_crossing_type, get_data_by_district

st.set_page_config(layout="wide")
st.title("NOC Dashboard")

# Load initial data
df = load_data()

# Session state initialization
if "clicked_type" not in st.session_state:
    st.session_state.clicked_type = None
if "clicked_district" not in st.session_state:
    st.session_state.clicked_district = None
if "clicked_status" not in st.session_state:
    st.session_state.clicked_status = None

# Show Crossing Types
crossing_types = df['Type of Crossing'].dropna().unique()
st.subheader("Type of Crossings")
cols = st.columns(len(crossing_types))
for i, ctype in enumerate(crossing_types):
    count = df[df['Type of Crossing'] == ctype].shape[0]
    if cols[i].button(f"{ctype} ({count})"):
        st.session_state.clicked_type = ctype
        st.session_state.clicked_district = None
        st.session_state.clicked_status = None

# Show Districts if type is clicked
if st.session_state.clicked_type:
    filtered_df = get_data_by_crossing_type(st.session_state.clicked_type)
    districts = filtered_df['District'].dropna().unique()
    st.subheader(f"Districts under {st.session_state.clicked_type}")
    cols = st.columns(len(districts))
    for i, dist in enumerate(districts):
        count = filtered_df[filtered_df['District'] == dist].shape[0]
        if cols[i].button(f"{dist} ({count})"):
            st.session_state.clicked_district = dist
            st.session_state.clicked_status = None

# Show NOC Status if district is clicked
if st.session_state.clicked_district:
    dist_df = get_data_by_district(st.session_state.clicked_district)
    received_df = dist_df[dist_df['NOC Status'].str.lower() == 'received']
    not_received_df = dist_df[dist_df['NOC Status'].str.lower() != 'received']
    received_count = len(received_df)
    not_received_count = len(not_received_df)

    st.subheader(f"NOC Status in {st.session_state.clicked_district}")
    col1, col2 = st.columns(2)

    if col1.button(f"Received ({received_count})"):
        st.session_state.clicked_status = "received"

    if col2.button(f"Not Received ({not_received_count})"):
        st.session_state.clicked_status = "not received"

    if st.session_state.clicked_status == "received":
        st.subheader("Received NOC Details")
        st.dataframe(received_df.reset_index(drop=True))

    elif st.session_state.clicked_status == "not received":
        st.subheader("Not Received NOC Details")
        for index, row in not_received_df.iterrows():
            col1, col2 = st.columns([4, 1])
            col1.write(f"{row['Area']}")
            if col2.button("Mark as Received", key=f"update_{index}"):
                update_noc_status(row['Area'])
                st.experimental_rerun()
        st.dataframe(not_received_df.reset_index(drop=True))
