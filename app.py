# ==========================================================
# CARGO TABLE
# ==========================================================

st.divider()

st.subheader("📋 Current cargo")


if st.session_state.cargo:


    cargo_table = pd.DataFrame(

        [

            {

                "Delete": False,

                "Description": item.description,

                "Quantity": item.quantity,

                "Width cm": int(item.width * 100),

                "Length cm": int(item.length * 100),

                "Height cm": int(item.height * 100),

                "Weight kg": item.weight,

                "Rotation": item.allow_rotation

            }

            for item in st.session_state.cargo

        ]

    )


    edited_table = st.data_editor(

        cargo_table,

        use_container_width=True,

        hide_index=True,

        column_config={

            "Delete": st.column_config.CheckboxColumn(

                "Delete"

            )

        }

    )


    col1, col2 = st.columns(2)



    with col1:

        if st.button("🗑 Delete selected cargo"):


            remaining = []


            for i, row in edited_table.iterrows():

                if not row["Delete"]:

                    remaining.append(

                        st.session_state.cargo[i]

                    )


            st.session_state.cargo = remaining

            st.session_state.solution = None

            st.rerun()



    with col2:

        if st.button("🗑 Clear all cargo"):


            st.session_state.cargo = []

            st.session_state.solution = None

            st.rerun()



else:

    st.info(

        "No cargo added"

    )