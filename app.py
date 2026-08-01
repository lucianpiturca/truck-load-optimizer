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
# PAGE CONFIG
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
# TRUCK SELECT
# ==========================================================


truck_name = st.sidebar.selectbox(

    "Truck type",

    list(TRUCKS.keys())

)


truck = TRUCKS[truck_name]



st.sidebar.info(

    f"""
{truck.name}

Inside:
{truck.trailer_width:.2f} m ×
{truck.trailer_length:.2f} m

Legal gross:
{truck.legal_gross/1000:.0f} tons
"""

)



# ==========================================================
# ADD CARGO
# ==========================================================

st.subheader("📦 Add Cargo")



with st.form("cargo_form"):


    col1, col2, col3 = st.columns(3)



    with col1:

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



    with col2:

        width = st.number_input(

            "Width (cm)",

            value=120

        )


        length = st.number_input(

            "Length (cm)",

            value=100

        )


    with col3:


        height = st.number_input(

            "Height (cm)",

            value=240

        )


        rotation = st.checkbox(

            "Allow rotation",

            value=True

        )



    add = st.form_submit_button(

        "➕ Add Cargo"

    )



    if add:


        st.session_state.cargo.append(

            CargoItem(

                description=description,

                quantity=int(quantity),

                width=width/100,

                length=length/100,

                height=height/100,

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


st.subheader("Current Cargo")



if st.session_state.cargo:


    table = pd.DataFrame([

        {

            "Delete": False,

            "Description": c.description,

            "Qty": c.quantity,

            "Width cm": int(c.width*100),

            "Length cm": int(c.length*100),

            "Height cm": int(c.height*100),

            "Weight kg": c.weight,

            "Rotation": c.allow_rotation

        }

        for c in st.session_state.cargo

    ])



    edited = st.data_editor(

        table,

        hide_index=True,

        use_container_width=True

    )



    if st.button(

        "🗑 Delete Selected"

    ):


        new = []


        for index,row in edited.iterrows():


            if not row["Delete"]:

                new.append(

                    st.session_state.cargo[index]

                )


        st.session_state.cargo = new


        st.rerun()



else:


    st.info(

        "No cargo added"

    )



# ==========================================================
# CLEAR
# ==========================================================


if st.button(

    "🧹 Clear all cargo"

):

    st.session_state.cargo = []

    st.session_state.solution = None

    st.rerun()



# ==========================================================
# OPTIMIZE
# ==========================================================


st.divider()



if st.button(

    "🚀 Optimize Load",

    type="primary"

):


    if not st.session_state.cargo:


        st.warning(

            "Add cargo first"

        )


    else:


        with st.spinner(

            "Optimizing..."

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



    # ------------------------------------------
    # choose solution
    # ------------------------------------------


    options = []


    if result.best:

        options.append(

            "🥇 Best solution"

        )


    if result.second_best:

        options.append(

            "🥈 Second best solution"

        )



    selected = st.radio(

        "Choose loading plan",

        options

    )



    if selected.startswith(

        "🥇"

    ):

        layout, axle_report = result.best



    else:

        layout, axle_report = result.second_best



    # ------------------------------------------
    # columns
    # ------------------------------------------


    left,right = st.columns(

        [1,1]

    )



    with left:


        st.pyplot(

            draw_trailer(

                truck,

                layout

            )

        )



    with right:


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