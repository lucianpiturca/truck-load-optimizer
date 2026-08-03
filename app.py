"""Streamlit application for the Truck Load Optimizer."""

import pandas as pd
import streamlit as st

from cargo import CargoItem
from drawing import create_loading_figure
from optimizer import optimize_load
from report import generate_report
from truck import TRUCKS


st.set_page_config(
    page_title="LoadPlan | Truck Load Optimizer",
    page_icon="L",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root { --navy: #102A43; --blue: #1F6FEB; --ink: #243B53; --muted: #627D98; --line: #D9E2EC; }
    .stApp { background: #F5F7FA; color: var(--ink); }
    [data-testid="stSidebar"] { background: #102A43; }
    [data-testid="stSidebar"] * { color: #F0F4F8; }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] > div { background: #F0F4F8 !important; border-color: #9FB3C8 !important; }
    [data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] > div > div,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] div,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] span,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] input { color: #243B53 !important; -webkit-text-fill-color: #243B53 !important; opacity: 1 !important; font-weight: 600 !important; }
    [data-baseweb="popover"] *, [role="listbox"] * { color: #243B53 !important; -webkit-text-fill-color: #243B53 !important; }
    [data-testid="stSidebar"] .stCaption { color: #BCCCDC !important; }
    .block-container { max-width: 1500px; padding-top: 2rem; padding-bottom: 3rem; }
    .hero { background: linear-gradient(115deg, #102A43, #1F4E79); border-radius: 18px; color: white; padding: 1.7rem 2rem; margin-bottom: 1.6rem; box-shadow: 0 12px 28px rgba(16,42,67,.15); }
    .hero h1 { font-size: 2rem; margin: 0; letter-spacing: -.03em; }
    .hero p { color: #D9EAF7; margin: .45rem 0 0; font-size: 1rem; }
    .section-label { color: #486581; font-size: .78rem; font-weight: 700; letter-spacing: .11em; text-transform: uppercase; margin-bottom: .2rem; }
    .stButton > button { border-radius: 8px; font-weight: 650; min-height: 2.55rem; }
    .stButton > button[kind="primary"] { background: #1F6FEB; border-color: #1F6FEB; }
    .stButton > button[kind="primary"]:hover { background: #175BC4; border-color: #175BC4; }
    [data-testid="stMetric"] { background: white; border: 1px solid #D9E2EC; border-radius: 12px; padding: .65rem .85rem; }
    [data-testid="stMetricLabel"] { color: #627D98; font-size: .82rem; }
    [data-testid="stMetricValue"] { color: #102A43; font-size: 1.5rem; }
    .stDataFrame { border: 1px solid #D9E2EC; border-radius: 10px; overflow: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

if "cargo" not in st.session_state:
    st.session_state.cargo = []
if "result" not in st.session_state:
    st.session_state.result = None

with st.sidebar:
    st.markdown("## LoadPlan")
    st.caption("TRAILER LOAD PLANNING")
    st.divider()
    st.markdown("#### Vehicle profile")
    truck_name = st.selectbox("Truck type", list(TRUCKS.keys()))
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

st.markdown(
    """
    <div class="hero">
        <h1>Truck Load Optimizer</h1>
        <p>Build a practical loading plan, verify axle limits, and visualize the finished trailer.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-label">Cargo entry</div>', unsafe_allow_html=True)
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
            st.rerun()

st.markdown('<div class="section-label">Load manifest</div>', unsafe_allow_html=True)
if st.session_state.cargo:
    total_units = sum(item.quantity for item in st.session_state.cargo)
    total_payload = sum(item.quantity * item.weight for item in st.session_state.cargo)
    m1, m2, m3 = st.columns(3)
    m1.metric("Cargo lines", len(st.session_state.cargo))
    m2.metric("Pallets requested", total_units)
    m3.metric("Payload requested", f"{total_payload:,.0f} kg")
    manifest = pd.DataFrame(
        [{
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
        st.write("")
        if st.button("Remove selected", use_container_width=True):
            st.session_state.cargo.pop(remove_index)
            st.session_state.result = None
            st.rerun()
else:
    st.info("Your manifest is empty. Add one or more cargo lines to create a loading plan.")

action_left, action_right = st.columns([3, 1])
with action_left:
    optimize = st.button("Optimize loading plan", type="primary", use_container_width=True, disabled=not st.session_state.cargo)
with action_right:
    if st.button("Clear manifest", use_container_width=True, disabled=not st.session_state.cargo):
        st.session_state.cargo = []
        st.session_state.result = None
        st.rerun()

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

        st.markdown("#### Compliance summary")
        st.code(generate_report(truck, result), language=None)
    else:
        st.error("No legal loading plan was found for the current manifest.")
        st.code(generate_report(truck, result), language=None)
