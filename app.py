import streamlit as st
import pandas as pd

from truck import TRUCKS

st.set_page_config(
    page_title="Truck Load Optimizer",
    layout="wide"
)

st.title("🚛 European 5-Axle Load Optimizer")

truck_name = st.sidebar.selectbox(
    "Truck Type",
    list(TRUCKS.keys())
)

truck = TRUCKS[truck_name]

st.sidebar.header("Trailer")

st.sidebar.write(f"Length : {truck.trailer_length:.2f} m")

st.sidebar.write(f"Width : {truck.trailer_width:.2f} m")

st.sidebar.write(f"Legal Gross : {truck.legal_gross} kg")

st.sidebar.header("Empty Axles")

for i, axle in enumerate(truck.empty_axles):

    st.sidebar.write(f"Axle {i+1}: {axle} kg")


if "cargo" not in st.session_state:

    st.session_state.cargo = pd.DataFrame(columns=[
        "Description",
        "Qty",
        "Width",
        "Length",
        "Weight",
        "Rotate"
    ])


st.subheader("Cargo Manifest")

edited = st.data_editor(
    st.session_state.cargo,
    num_rows="dynamic",
    use_container_width=True
)

st.session_state.cargo = edited

st.write("")

st.subheader("Trailer Layout")

st.info("Trailer drawing will appear here in Part 2.")

st.write("")

st.subheader("Scale Report")

gross = sum(
    edited["Qty"] * edited["Weight"]
) if len(edited) else 0

st.metric(
    "Cargo Weight",
    f"{gross:,.0f} kg"
)

total = gross + sum(truck.empty_axles)

st.metric(
    "Gross Vehicle Weight",
    f"{total:,.0f} kg"
)