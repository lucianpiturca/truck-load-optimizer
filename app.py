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
# TRUCK
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

Width:
{truck.trailer_width:.2f} m

Length:
{truck.trailer_length:.2f} m

Maximum gross:
{truck.legal_gross/1000:.0f} t
"""

)



# ==========================================================
# ADD CARGO
# ==========================================================

st.subheader("📦 Add cargo")


with st.form("cargo_form"):


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


    add_cargo = st.form_submit_button(

        "➕ Add cargo"

    )



    if add_cargo:


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


        st.session_state.solution = None


        st.success(

            "Cargo added"

        )



# ==========================================================
# CARGO TABLE
# ==========================================================

st.divider()

st.subheader("📋 Cargo list")



if st.session_state.cargo:


    cargo_table = pd.DataFrame(

        [

            {

                "Delete": False,

                "Description": c.description,

                "Quantity": c.quantity,

                "Width (cm)": int(c.width*100),

                "Length (cm)": int(c.length*100),

                "Height (cm)": int(c.height*100),

                "Weight (kg)": c.weight,

                "Rotation": c.allow_rotation

            }

            for c in st.session_state.cargo

        ]

    )


    edited = st.data_editor(

        cargo_table,

        hide_index=True,

        use_container_width=True,

        column_config={

            "Delete":

            st.column_config.CheckboxColumn(

                "Delete"

            )

        }

    )


    col1, col2 = st.columns(2)


    with col1:


        if st.button(

            "🗑 Delete selected"

        ):


            new_list = []


            for i, row in edited.iterrows():


                if not row["Delete"]:

                    new_list.append(

                        st.session_state.cargo[i]

                    )


            st.session_state.cargo = new_list

            st.session_state.solution = None

            st.rerun()



    with col2:


        if st.button(

            "🗑 Delete all"

        ):


            st.session_state.cargo = []

            st.session_state.solution = None

            st.rerun()



else:


    st.info(

        "No cargo entered"

    )



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

            "Optimizing load..."

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


    layout = result.best[0]


    axle_report = result.best[1]



    left, right = st.columns(

        [0.8, 1.2]

    )


    with left:


        st.subheader(

            "Trailer visualization"

        )


        st.pyplot(

            draw_trailer(

                truck,

                layout

            ),

            use_container_width=False

        )



    with right:


        st.subheader(

            "Reports"

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