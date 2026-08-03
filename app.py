# ==========================================================
# app.py
# Truck Load Optimizer
# ==========================================================


import streamlit as st


from truck import TRUCKS

from cargo import CargoItem

from optimizer import optimize_load

from drawing import create_loading_figure

from report import generate_report



# ==========================================================
# PAGE SETTINGS
# ==========================================================


st.set_page_config(

    page_title="Truck Load Optimizer",

    layout="wide"

)



# ==========================================================
# SESSION STATE
# ==========================================================


if "cargo" not in st.session_state:

    st.session_state.cargo = []


if "result" not in st.session_state:

    st.session_state.result = None



# ==========================================================
# TITLE
# ==========================================================


st.title(
    "🚛 Truck Load Optimizer"
)



# ==========================================================
# SIDEBAR
# ==========================================================


st.sidebar.header(
    "Truck"
)


truck_name = st.sidebar.selectbox(

    "Select truck",

    list(TRUCKS.keys())

)


truck = TRUCKS[truck_name]



# ==========================================================
# ADD CARGO
# ==========================================================


st.subheader(
    "➕ Add Cargo"
)



c1, c2, c3, c4, c5, c6 = st.columns(6)



with c1:

    description = st.text_input(
        "Description"
    )


with c2:

    length = st.number_input(
        "Length cm",
        min_value=1,
        value=120
    )


with c3:

    width = st.number_input(
        "Width cm",
        min_value=1,
        value=80
    )


with c4:

    height = st.number_input(
        "Height cm",
        min_value=1,
        value=160
    )


with c5:

    weight = st.number_input(
        "Weight kg",
        min_value=1,
        value=1000
    )


with c6:

    quantity = st.number_input(
        "Quantity",
        min_value=1,
        value=1
    )



if st.button(
    "Add cargo"
):

    st.session_state.cargo.append(

        CargoItem(

            description=description,

            quantity=int(quantity),

            length=length / 100,

            width=width / 100,

            height=height / 100,

            weight=weight

        )

    )


    st.session_state.result = None



# ==========================================================
# CARGO LIST
# ==========================================================


st.subheader(
    "📦 Cargo list"
)



if st.session_state.cargo:


    for index, item in enumerate(

        st.session_state.cargo

    ):


        cols = st.columns(
            [4,2,2,2,2,1]
        )


        cols[0].write(
            item.description
        )


        cols[1].write(
            f"{item.length:.2f} x {item.width:.2f}"
        )


        cols[2].write(
            f"{item.weight} kg"
        )


        cols[3].write(
            f"x {item.quantity}"
        )


        if cols[5].button(

            "❌",

            key=f"delete_{index}"

        ):

            st.session_state.cargo.pop(index)

            st.session_state.result = None

            st.rerun()



else:

    st.info(
        "No cargo added"
    )



if st.button(
    "🗑 Clear all cargo"
):

    st.session_state.cargo = []

    st.session_state.result = None

    st.rerun()



# ==========================================================
# OPTIMIZE + REPORT + VISUALIZATION
# ==========================================================


st.divider()



left_col, right_col = st.columns(
    [1, 2]
)



# ==========================================================
# LEFT SIDE
# ==========================================================


with left_col:


    if st.button(

        "🚀 Optimize Load",

        type="primary"

    ):


        st.session_state.result = optimize_load(

            truck,

            st.session_state.cargo

        )



    if st.session_state.result:


        st.subheader(

            "📊 Loading Result"

        )


        st.text(

            generate_report(

                truck,

                st.session_state.result

            )

        )



# ==========================================================
# RIGHT SIDE
# ==========================================================


with right_col:


    if st.session_state.result:


        if st.session_state.result.success:


            st.subheader(

                "🚛 Load Visualization"

            )


            layout = st.session_state.result.best[0]


            fig = create_loading_figure(

                truck,

                layout

            )


            st.plotly_chart(

                fig,

                use_container_width=True,

                config={

                    "displayModeBar": False

                }

            )