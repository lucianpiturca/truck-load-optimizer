import streamlit as st
import pandas as pd

from optimizer import optimize_load

from truck import TRUCKS

from packing import pack_cargo

from drawing import draw_trailer

from axles import (
    calculate_axle_loads,
    check_axles,
    calculate_gross_weight
)



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
# Cargo table
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

st.info(
    "Optimizer priority: Height → Weight → Axle legality → Space efficiency"
)

# ---------------------------------
# Packing
# ---------------------------------

if st.button("🚀 Optimize Load"):

    st.session_state.optimized = True



if "optimized" in st.session_state:

    pallets = optimize_load(

        truck,

        edited

    )

else:

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

    f"{used_length / truck.trailer_length * 100:.1f}%"

)



# ---------------------------------
# Axle calculations
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



# ---------------------------------
# Axle report
# ---------------------------------

st.subheader(
    "⚖️ Axle Weight Report"
)



for index, axle in enumerate(

    axle_results

):


    percentage = (

        axle["weight"]

        /

        axle["limit"]

    )


    text = (

        f"Axle {index+1}: "

        f"{axle['weight']:,.0f} kg "

        f"/ "

        f"{axle['limit']:,.0f} kg"

    )


    if axle["legal"]:

        st.success(

            "🟢 " + text

        )

    else:

        st.error(

            "🔴 " + text + " OVERWEIGHT"

        )



# ---------------------------------
# Total weight
# ---------------------------------

st.subheader(
    "🚛 Total Weight"
)



if gross <= truck.legal_gross:

    st.success(

        f"🟢 Total {gross:,.0f} kg / "
        f"{truck.legal_gross:,.0f} kg"

    )


else:

    st.error(

        f"🔴 Total {gross:,.0f} kg / "
        f"{truck.legal_gross:,.0f} kg"

    )