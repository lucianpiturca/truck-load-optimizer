import streamlit as st
import pandas as pd


from truck import TRUCKS

from packing import pack_cargo

from drawing import draw_trailer

from axles import (
    calculate_axle_loads,
    check_axles,
    calculate_gross_weight
)

from optimizer import optimize_load



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
# Truck selection
# ---------------------------------

truck_name = st.sidebar.selectbox(

    "Truck Type",

    list(TRUCKS.keys())

)


truck = TRUCKS[truck_name]



# ---------------------------------
# Truck info
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


for i, axle in enumerate(truck.empty_axles):

    st.sidebar.write(
        f"Axle {i+1}: {axle:,} kg"
    )



# ---------------------------------
# Cargo input
# ---------------------------------

st.subheader(
    "📦 Add Cargo"
)


if "cargo" not in st.session_state:

    st.session_state.cargo = pd.DataFrame(

        columns=[

            "Goods Description",
            "Pallet Quantity",
            "Width (cm)",
            "Length (cm)",
            "Height (cm)",
            "Weight (kg)",
            "Allow Rotation"

        ]

    )


with st.form("cargo_form"):


    col1, col2, col3 = st.columns(3)


    with col1:

        description = st.text_input(
            "Goods Description"
        )

        quantity = st.number_input(
            "Pallet Quantity",
            min_value=1,
            value=1,
            step=1
        )


    with col2:

        width = st.number_input(
            "Width (cm)",
            min_value=1,
            value=120,
            step=1
        )


        length = st.number_input(
            "Length (cm)",
            min_value=1,
            value=80,
            step=1
        )


    with col3:

        height = st.number_input(
            "Height (cm)",
            min_value=1,
            value=240,
            step=1
        )


        weight = st.number_input(
            "Weight (kg)",
            min_value=1,
            value=1000,
            step=1
        )


    rotation = st.checkbox(
        "Allow Rotation",
        value=True
    )


    submitted = st.form_submit_button(
        "➕ Add Cargo"
    )



if submitted:


    new_row = pd.DataFrame(

        [
            {

                "Goods Description": description,

                "Pallet Quantity": quantity,

                "Width (cm)": width,

                "Length (cm)": length,

                "Height (cm)": height,

                "Weight (kg)": weight,

                "Allow Rotation": rotation

            }

        ]

    )


    st.session_state.cargo = pd.concat(

        [
            st.session_state.cargo,
            new_row
        ],

        ignore_index=True

    )



st.subheader(
    "Current Cargo"
)


st.dataframe(

    st.session_state.cargo,

    hide_index=True,

    use_container_width=True

)


# ---------------------------------
# Optimizer
# ---------------------------------

st.info(
    "Optimization priority: Height → Weight → Axle legality → Space efficiency"
)



if st.button(
    "🚀 Optimize Load"
):

    st.session_state.optimized = True



if "optimized" in st.session_state:


    pallets = optimize_load(

        truck,

        st.session_state.cargo

    )


else:


    pallets = pack_cargo(

        truck,

        st.session_state.cargo

    )



# ---------------------------------
# Trailer drawing
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


c1, c2, c3 = st.columns(3)


c1.metric(

    "Used Length",

    f"{used_length:.2f} m"

)


c2.metric(

    "Free Length",

    f"{free_length:.2f} m"

)


c3.metric(

    "Utilization",

    f"{used_length/truck.trailer_length*100:.1f}%"

)



# ---------------------------------
# Axle report
# ---------------------------------

axle_loads = calculate_axle_loads(

    truck,

    pallets

)


axle_results = check_axles(

    truck,

    axle_loads

)


gross = calculate_gross_weight(

    axle_loads

)



st.subheader(
    "⚖️ Axle Weight Report"
)



for i, axle in enumerate(axle_results):


    message = (

        f"Axle {i+1}: "

        f"{axle['weight']:,.0f} kg "

        f"/ "

        f"{axle['limit']:,.0f} kg"

    )


    if axle["legal"]:

        st.success(
            "🟢 " + message
        )

    else:

        st.error(
            "🔴 " + message + " OVERWEIGHT"
        )



# ---------------------------------
# Total weight
# ---------------------------------

st.subheader(
    "🚛 Total Weight"
)



if gross <= truck.legal_gross:


    st.success(

        f"🟢 Total: {gross:,.0f} kg / "
        f"{truck.legal_gross:,.0f} kg"

    )


else:


    st.error(

        f"🔴 Total: {gross:,.0f} kg / "
        f"{truck.legal_gross:,.0f} kg"

    )