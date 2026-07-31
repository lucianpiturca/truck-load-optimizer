import streamlit as st
import pandas as pd


from truck import TRUCKS

from packing import (
    pack_cargo,
    calculate_used_length
)

from drawing import draw_trailer



# ---------------------------------
# Page setup
# ---------------------------------

st.set_page_config(
    page_title="Truck Load Optimizer",
    layout="wide"
)


st.title(
    "🚛 European Truck Load Optimizer"
)



# ---------------------------------
# Select truck
# ---------------------------------

truck_name = st.sidebar.selectbox(

    "Truck Type",

    list(TRUCKS.keys())

)


truck = TRUCKS[truck_name]



# ---------------------------------
# Truck information
# ---------------------------------

st.sidebar.header(
    "Trailer Information"
)


st.sidebar.write(
    f"Length: {truck.trailer_length:.2f} m"
)


st.sidebar.write(
    f"Width: {truck.trailer_width:.2f} m"
)


st.sidebar.write(
    f"Legal GVW: {truck.legal_gross:,} kg"
)



st.sidebar.header(
    "Empty Axle Weights"
)


for i, axle in enumerate(
    truck.empty_axles
):

    st.sidebar.write(

        f"Axle {i+1}: {axle:,} kg"

    )



# ---------------------------------
# Cargo manifest
# ---------------------------------

st.subheader(
    "📦 Cargo Manifest"
)



if "cargo" not in st.session_state:


    st.session_state.cargo = pd.DataFrame(

        columns=[

            "Description",

            "Qty",

            "Width",

            "Length",

            "Height",

            "Weight",

            "Rotate"

        ]

    )



edited = st.data_editor(

    st.session_state.cargo,

    num_rows="dynamic",

    use_container_width=True

)



st.session_state.cargo = edited



# ---------------------------------
# Packing
# ---------------------------------

pallets = pack_cargo(

    truck,

    edited

)



# ---------------------------------
# Drawing
# ---------------------------------

st.subheader(
    "📐 Trailer Layout"
)



fig, used_length, free_length = draw_trailer(

    truck,

    pallets

)


st.pyplot(

    fig,

    use_container_width=True

)



# ---------------------------------
# Space report
# ---------------------------------

st.subheader(
    "📏 Trailer Utilization"
)



col1, col2, col3 = st.columns(3)



col1.metric(

    "Used Length",

    f"{used_length:.2f} m"

)


col2.metric(

    "Free Length",

    f"{free_length:.2f} m"

)


col3.metric(

    "Utilization",

    f"{used_length/truck.trailer_length*100:.1f}%"

)



# ---------------------------------
# Weight calculation
# ---------------------------------

st.subheader(
    "⚖️ Weight Summary"
)



cargo_weight = 0


for pallet in pallets:

    cargo_weight += pallet["weight"]



empty_weight = sum(

    truck.empty_axles

)



gross_weight = (

    cargo_weight

    +

    empty_weight

)



col1, col2 = st.columns(2)



col1.metric(

    "Cargo Weight",

    f"{cargo_weight:,.0f} kg"

)


col2.metric(

    "Gross Vehicle Weight",

    f"{gross_weight:,.0f} kg"

)



# ---------------------------------
# Status
# ---------------------------------

if gross_weight <= truck.legal_gross:


    st.success(

        "🟢 Gross weight is legal"

    )

else:


    st.error(

        "🔴 Gross weight exceeds 40 tons"

    )