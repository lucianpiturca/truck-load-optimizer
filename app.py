"""Streamlit application for the Truck Load Optimizer.

Updated: modernized UI, cargo template download/upload, and visualization PDF export.
"""

import io
import datetime

import pandas as pd
import streamlit as st

from cargo import CargoItem
from drawing import create_loading_figure, save_figure_pdf
from optimizer import optimize_load
from report import generate_report
from truck import TRUCKS


st.set_page_config(
    page_title="LoadPlan | Truck Load Optimizer",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Simple top-bar styling ---
st.markdown(
    """
    <style>
    :root { --navy: #102A43; --blue: #1F6FEB; --ink: #243B53; --muted: #627D98; --line: #D9E2EC; }
    .stApp { background: #F7FAFC; color: var(--ink); }
    .app-header { background: linear-gradient(115deg, #102A43, #1F4E79); border-radius: 12px; color: white; padding: 14px 18px; margin-bottom: 12px; }
    .app-sub { color: #D9EAF7; margin-top:6px; font-size:0.95rem }
    .small-muted { color: #627D98; font-size: .85rem }
    </style>
    """,
    unsafe_allow_html=True,
)

if "cargo" not in st.session_state:
    st.session_state.cargo = []
if "result" not in st.session_state:
    st.session_state.result = None

# --- Header ---
with st.container():
    st.markdown('<div class="app-header">', unsafe_allow_html=True)
    c1, c2 = st.columns([8, 2])
    with c1:
        st.markdown("<h2 style='margin:0;color:white'>Truck Load Optimizer</h2>", unsafe_allow_html=True)
        st.markdown("<div class='app-sub'>Build loading plans, validate axle limits, and export a printable visualization.</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Sidebar: truck profile ---
with st.sidebar:
    st.markdown("## Vehicle profile")
    truck_name = st.radio("Truck type", list(TRUCKS.keys()), horizontal=True)
    truck = TRUCKS[truck_name]
    st.caption("Internal loading space")
    st.markdown(f"**{truck.trailer_length:.2f} m × {truck.trailer_width:.2f} m**")
    st.caption("Maximum cargo height")
    st.markdown(f"**{truck.trailer_height:.2f} m**")
    st.caption("Maximum combination weight")
    st.markdown(f"**{truck.legal_gross:,.0f} kg**")
    st.caption("Trailer axle group centre")
    st.markdown(f"**{truck.bogie_position:.2f} m behind kingpin**")
    st.divider()
    st.caption("Static, level-ground planning model. Confirm final axle weights on an approved weighbridge.")

# --- Main layout: tabs for manifest and optimization ---
tab_manifest, tab_optimize = st.tabs(["Edit manifest / Upload template", "Optimize & Results"])

# Helper: generate template dataframe (3 pallet types + header guidance)
TEMPLATE_COLUMNS = ["Description", "Quantity", "Length_cm", "Width_cm", "Height_cm", "Weight_kg", "AllowRotation"]

def generate_template_df():
    return pd.DataFrame(
        [
            {
                "Description": "Europallet",
                "Quantity": 1,
                "Length_cm": 120,
                "Width_cm": 80,
                "Height_cm": 160,
                "Weight_kg": 1000,
                "AllowRotation": True,
            },
            {
                "Description": "Industrial pallet",
                "Quantity": 1,
                "Length_cm": 120,
                "Width_cm": 100,
                "Height_cm": 160,
                "Weight_kg": 1200,
                "AllowRotation": True,
            },
            {
                "Description": "Custom pallet (edit sizes)",
                "Quantity": 1,
                "Length_cm": 0,
                "Width_cm": 0,
                "Height_cm": 0,
                "Weight_kg": 0,
                "AllowRotation": True,
            },
        ],
        columns=TEMPLATE_COLUMNS,
    )


def template_csv_bytes():
    return generate_template_df().to_csv(index=False).encode("utf-8")


def template_xlsx_bytes():
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        generate_template_df().to_excel(writer, index=False, sheet_name="template")
    buffer.seek(0)
    return buffer.read()


def dataframe_to_cargo_items(df, truck):
    items = []
    errors = []

    for idx, row in df.iterrows():
        row_no = idx + 1
        try:
            desc = str(row.get("Description", "")).strip()
            qty = int(row.get("Quantity", 0))
            length_cm = float(row.get("Length_cm", 0))
            width_cm = float(row.get("Width_cm", 0))
            height_cm = float(row.get("Height_cm", 0))
            weight = float(row.get("Weight_kg", 0))
            allow_rotation = row.get("AllowRotation", True)
            if str(allow_rotation).strip().lower() in ("false", "0", "no"):
                allow_rotation = False
            else:
                allow_rotation = True

            if not desc:
                errors.append(f"Row {row_no}: Description is empty")
                continue
            if qty <= 0:
                errors.append(f"Row {row_no}: Quantity must be >= 1")
                continue
            if length_cm <= 0 or width_cm <= 0 or height_cm <= 0:
                errors.append(f"Row {row_no}: Dimensions must be positive (cm)")
                continue
            if weight <= 0:
                errors.append(f"Row {row_no}: Weight must be positive (kg)")
                continue

            item = CargoItem(
                description=desc,
                quantity=int(qty),
                length=length_cm / 100.0,
                width=width_cm / 100.0,
                height=height_cm / 100.0,
                weight=weight,
                allow_rotation=allow_rotation,
            )
            v = item.validate(truck)
            if v:
                errors.append(f"Row {row_no}: " + "; ".join(v))
            else:
                items.append(item)
        except Exception as e:
            errors.append(f"Row {row_no}: parse error: {e}")

    return items, errors

# --- Manifest tab ---
with tab_manifest:
    st.markdown("### Manifest and templates")
    cleft, cright = st.columns([3, 1])
    with cright:
        st.markdown("#### Download template")
        st.download_button("Template (CSV)", data=template_csv_bytes(), file_name="cargo_template.csv", mime="text/csv")
        st.download_button("Template (Excel)", data=template_xlsx_bytes(), file_name="cargo_template.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.divider()
        st.markdown("#### Upload filled template")
        uploaded = st.file_uploader("Upload CSV or XLSX file", type=["csv", "xlsx"], accept_multiple_files=False)
        if uploaded is not None:
            try:
                if uploaded.name.lower().endswith(".csv"):
                    df = pd.read_csv(uploaded)
                else:
                    df = pd.read_excel(uploaded)

                missing = [c for c in TEMPLATE_COLUMNS if c not in df.columns]
                if missing:
                    st.error(f"Missing columns: {', '.join(missing)}. Template header is required.")
                else:
                    items, errors = dataframe_to_cargo_items(df, truck)
                    if errors:
                        st.error("Errors found in uploaded file:")
                        for e in errors:
                            st.write(f"- {e}")
                    else:
                        st.session_state.cargo = items
                        st.session_state.result = None
                        st.success(f"Imported {sum(i.quantity for i in items)} pallets from upload.")
                        st.experimental_rerun()
            except Exception as e:
                st.error(f"Failed to read uploaded file: {e}")

    with cleft:
        st.markdown("#### Cargo entry (manual)")
        with st.form("cargo_entry", clear_on_submit=True):
            c1, c2, c3 = st.columns([2.1, 1, 1])
            with c1:
                description = st.text_input("Cargo description", placeholder="e.g. Beverage pallets")
            with c2:
                quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
            with c3:
                weight = st.number_input("Weight per pallet (kg)", min_value=1, value=1000, step=25)
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                length = st.number_input("Length (cm)", min_value=1, value=120, step=1)
            with c2:
                width = st.number_input("Width (cm)", min_value=1, value=80, step=1)
            with c3:
                height = st.number_input("Height (cm)", min_value=1, value=160, step=1)
            with c4:
                st.caption("Dimensions are entered per pallet.")
            with c5:
                add_cargo = st.form_submit_button("Add cargo", use_container_width=True)
            if add_cargo:
                item = CargoItem(
                    description=description.strip() or "Unlabelled cargo",
                    quantity=int(quantity),
                    length=length / 100,
                    width=width / 100,
                    height=height / 100,
                    weight=weight,
                )
                errors = item.validate(truck)
                if errors:
                    st.error(" · ".join(errors))
                else:
                    st.session_state.cargo.append(item)
                    st.session_state.result = None
                    st.experimental_rerun()

    st.markdown("#### Current manifest")
    if st.session_state.cargo:
        total_units = sum(item.quantity for item in st.session_state.cargo)
        total_payload = sum(item.quantity * item.weight for item in st.session_state.cargo)
        m1, m2, m3 = st.columns(3)
        m1.metric("Cargo lines", len(st.session_state.cargo))
        m2.metric("Pallets requested", total_units)
        m3.metric("Payload requested", f"{total_payload:,.0f} kg")
        manifest = pd.DataFrame([
            {
                "Description": item.description,
                "Quantity": item.quantity,
                "Footprint": f"{item.length:.2f} × {item.width:.2f} m",
                "Height": f"{item.height:.2f} m",
                "Weight / pallet": f"{item.weight:,.0f} kg",
                "Line weight": f"{item.quantity * item.weight:,.0f} kg",
            } for item in st.session_state.cargo]
        )
        st.dataframe(manifest, hide_index=True, use_container_width=True)
        remove_left, remove_right = st.columns([3, 1])
        with remove_left:
            remove_index = st.selectbox(
                "Remove a cargo line", range(len(st.session_state.cargo)),
                format_func=lambda i: f"{i + 1}. {st.session_state.cargo[i].description}",
            )
        with remove_right:
            if st.button("Remove selected", use_container_width=True):
                st.session_state.cargo.pop(remove_index)
                st.session_state.result = None
                st.experimental_rerun()
    else:
        st.info("Your manifest is empty. Add one or more cargo lines or upload a template.")

# --- Optimization tab ---
with tab_optimize:
    st.markdown("### Optimization & results")
    action_left, action_right = st.columns([3, 1])
    with action_left:
        optimize = st.button("Optimize loading plan", type="primary", use_container_width=True, disabled=not st.session_state.cargo)
    with action_right:
        if st.button("Clear manifest", use_container_width=True, disabled=not st.session_state.cargo):
            st.session_state.cargo = []
            st.session_state.result = None
            st.experimental_rerun()

    if optimize:
        with st.spinner("Evaluating loading patterns and axle weights..."):
            st.session_state.result = optimize_load(truck, st.session_state.cargo)

    if st.session_state.result:
        result = st.session_state.result
        st.divider()
        st.markdown('<div class="section-label">Optimization result</div>', unsafe_allow_html=True)
        if result.success:
            st.success("A legal loading plan was found.")
            layout = result.best[0]
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Loaded", f"{result.loaded_pallets} / {result.requested_pallets}")
            r2.metric("Trailer used", f"{layout.used_length:.2f} m")
            r3.metric("Free length", f"{layout.free_length:.2f} m")
            r4.metric("Load pattern", layout.pattern_name)
            st.markdown("#### Trailer load plan")
            st.caption("Front bulkhead is on the left. Hover a pallet for its full details.")
            fig = create_loading_figure(truck, layout)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            # PDF download for visualization only
            pdf_bytes = None
            try:
                pdf_bytes = save_figure_pdf(fig)
            except Exception as e:
                st.warning(f"PDF export currently unavailable: {e}")

            if pdf_bytes:
                now = datetime.datetime.now().strftime("%Y%m%d_%H%M")
                st.download_button(
                    label="Download visualization (PDF)",
                    data=pdf_bytes,
                    file_name=f"loadplan_{now}.pdf",
                    mime="application/pdf",
                )

            st.markdown("#### Compliance summary")
            st.code(generate_report(truck, result), language=None)
        else:
            st.error("No legal loading plan was found for the current manifest.")
            st.code(generate_report(truck, result), language=None)

