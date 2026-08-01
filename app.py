# app.py

import streamlit as st
import pandas as pd


from truck import TRUCKS

from cargo import CargoItem

from optimizer import optimize_load

from drawing import draw_trailer

from report import (
    generate_axle_report,
    generate_load_summary,
    generate_rejected_report
)



# ==========================================================
# PAGE SETTINGS
# ==========================================================

st.set_page_config(

    page_title="Truck Load Optimizer",

    layout="wide"

)


st.title("🚛 Truck Load Optimizer")



# ==========================================================
# SESSION STATE
# ==========================================================

if "cargo" not in st.session_state:

    st.session_state.cargo = []


if "solution" not in st.session_state:

    st.session_state.solution = None



# ==========================================================
# TRUCK SELECTION
# ==========================================================

st.sidebar.header("Truck configuration")


truck_name = st.sidebar.selectbox(

    "Select truck",

    list(TRUCKS.keys())

)


truck = TRUCKS[truck_name]



st.sidebar.info(

    f"""
**{truck.name}**

Inside dimensions:

{truck.trailer_width:.2f} m ×
{truck.trailer_length:.2f} m

Maximum gross:

{truck.legal_gross/1000:.0f} tons
"""

)



# ==========================================================
# ADD CARGO
# ==========================================================

st.subheader("📦 Cargo input")


with st.form(

    "cargo_form",

    clear_on_submit=True

):


    c1, c2, c3 = st.columns(3)


    with c1:


        description = st.text_input(

            "Goods description"

        )


        quantity = st.number_input(

            "Pallet quantity",

            min_value=1,

            value=1

        )


        weight = st.number_input(

            "Weight per pallet (kg)",

            min_value=1,

            value=1000

        )


    with c2:


        width = st.number_input(

            "Width (cm)",

            min_value=1,

            value=120

        )


        length = st.number_input(

            "Length (cm)",

            min_value=1,

            value=100

        )


    with c3:


        height = st.number_input(

            "Height (cm)",

            min_value=1,

            value=240

        )


        rotation = st.checkbox(

            "Allow rotation",

            value=True

        )



    add = st.form_submit_button(

        "➕ Add cargo"

    )


    if add:


        st.session_state.cargo.append(

            CargoItem(

                description=description,

                quantity=int(quantity),

                width=float(width)/100,

                length=float(length)/100,

                height=float(height)/100,

                weight=float(weight),

                allow_rotation=rotation

            )

        )


        st.success(

            "Cargo added"

        )



# ==========================================================
# CARGO TABLE
# ==========================================================

st.divider()

st.subheader("📋 Current cargo")



if st.session_state.cargo:


    cargo_table = pd.DataFrame(

        [

            {

                "Description": item.description,

                "Quantity": item.quantity,

                "Width cm": int(item.width*100),

                "Length cm": int(item.length*100),

                "Height cm": int(item.height*100),

                "Weight kg": item.weight,

                "Rotation": item.allow_rotation

            }

            for item in st.session_state.cargo

        ]

    )


    st.dataframe(

        cargo_table,

        use_container_width=True,

        hide_index=True

    )


    if st.button(

        "🗑 Clear all cargo"

    ):


        st.session_state.cargo = []

        st.session_state.solution = None

        st.rerun()



else:


    st.info(

        "No cargo added"

    )



# ==========================================================
# OPTIMIZE
# ==========================================================

st.divider()


if st.button(

    "🚀 Optimize Load",

    type="primary"

):


    if len(st.session_state.cargo) == 0:


        st.warning(

            "Please add cargo first."

        )


    else:


        with st.spinner(

            "Calculating loading solutions..."

        ):


            st.session_state.solution = optimize_load(

                truck,

                st.session_state.cargo

            )




# ==========================================================
# RESULTS
# ==========================================================

if st.session_state.solution:


    result = st.session_state.solution


    st.divider()


    # ---------------------------------------------
    # Select solution
    # ---------------------------------------------

    solutions = []


    if result.best:

        solutions.append(

            "🥇 Best solution"

        )


    if result.second_best:

        solutions.append(

            "🥈 Alternative solution"

        )


    if solutions:


        selected = st.radio(

            "Loading plan",

            solutions

        )


        if selected.startswith("🥇"):

            layout, axle_report = result.best


        else:

            layout, axle_report = result.second_best



    else:


        st.error(

            "No solution generated."

        )

        st.stop()



    # ---------------------------------------------
    # Display
    # ---------------------------------------------


    col_visual, col_report = st.columns(

        [0.8, 1.2]

    )


    with col_visual:


        st.subheader(

            "Trailer layout"

        )


        st.pyplot(

            draw_trailer(

                truck,

                layout

            ),

            use_container_width=False

        )



    with col_report:


        st.subheader(

            "Load report"

        )


        st.markdown(

            generate_load_summary(

                layout

            )

        )


        st.markdown(

            generate_axle_report(

                axle_report

            )

        )


        st.markdown(

            generate_rejected_report(

                result.rejected

            )

        )



st.caption(

    "Optimizer priority: legality → axle balance → height → weight → space efficiency"

)