# app.py
# Truck Load Optimizer 2.0


import streamlit as st


from truck import (
    CURTAINSIDER,
    FRIGO
)


from cargo import (
    CargoItem,
    expand_cargo
)


from optimizer import (
    optimize_load
)


from drawing import (
    create_loading_figure
)


from report import (
    generate_report
)



# ==========================================================
# PAGE CONFIG
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


if "solution" not in st.session_state:

    st.session_state.solution = None



# ==========================================================
# TITLE
# ==========================================================

st.title(
    "🚛 Truck Load Optimizer"
)



# ==========================================================
# TRUCK SELECT
# ==========================================================

truck_name = st.selectbox(

    "Truck type",

    [
        "Curtainsider",
        "Frigo"
    ]

)



truck = (

    CURTAINSIDER

    if truck_name == "Curtainsider"

    else FRIGO

)



# ==========================================================
# ADD CARGO
# ==========================================================


st.subheader(
    "📦 Add Cargo"
)



with st.form("cargo_form"):


    description = st.text_input(

        "Description"

    )


    quantity = st.number_input(

        "Quantity",

        min_value=1,

        value=1

    )


    col1, col2, col3 = st.columns(3)



    with col1:

        length = st.number_input(

            "Length (m)",

            value=1.20,

            step=0.01

        )


    with col2:

        width = st.number_input(

            "Width (m)",

            value=0.80,

            step=0.01

        )


    with col3:

        height = st.number_input(

            "Height (m)",

            value=1.50,

            step=0.01

        )


    weight = st.number_input(

        "Weight per pallet (kg)",

        value=1000,

        step=50

    )


    rotation = st.checkbox(

        "Allow rotation",

        value=True

    )



    submitted = st.form_submit_button(

        "Add Cargo"

    )



    if submitted:


        item = CargoItem(

            description=description,

            quantity=int(quantity),

            length=length,

            width=width,

            height=height,

            weight=weight,

            allow_rotation=rotation

        )


        errors = item.validate(

            truck

        )


        if errors:

            for e in errors:

                st.error(e)


        else:


            st.session_state.cargo.append(

                item

            )


            st.success(

                "Cargo added"

            )


            st.session_state.solution = None



# ==========================================================
# CURRENT CARGO TABLE
# ==========================================================


st.subheader(

    "Current Cargo"

)



if st.session_state.cargo:


    for index, item in enumerate(

        st.session_state.cargo

    ):


        cols = st.columns(

            [4,2,2,2,1]

        )


        cols[0].write(

            item.description

        )


        cols[1].write(

            f"{item.quantity} pcs"

        )


        cols[2].write(

            f"{item.length:.2f} × "
            f"{item.width:.2f}"

        )


        cols[3].write(

            f"{item.weight} kg"

        )


        if cols[4].button(

            "🗑️",

            key=f"delete_{index}"

        ):


            st.session_state.cargo.pop(

                index

            )


            st.session_state.solution = None


            st.rerun()



    if st.button(

        "Clear all cargo"

    ):


        st.session_state.cargo = []

        st.session_state.solution = None

        st.rerun()



else:

    st.info(

        "No cargo added."

    )



# ==========================================================
# OPTIMIZE
# ==========================================================


st.divider()



if st.button(

    "⚙️ Optimize Load",

    type="primary"

):


    pallets = expand_cargo(

        st.session_state.cargo

    )


    st.session_state.solution = optimize_load(

        truck,

        pallets

    )



# ==========================================================
# RESULTS
# ==========================================================


if st.session_state.solution:


    result = st.session_state.solution



    st.divider()



    st.subheader(

        "📊 Report"

    )


    st.text(

        generate_report(

            result,

            truck

        )

    )



    if result.best:


        st.subheader(

            "🚛 Loading Visualization"

        )


        fig = create_loading_figure(

            truck,

            result.best

        )


        st.plotly_chart(

            fig,

            use_container_width=True

        )