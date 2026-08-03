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
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

    :root {
        --paper: #FAFAF6;
        --panel: #FFFFFF;
        --ink: #1B2430;
        --steel: #5C6B7A;
        --blueprint: #2B5D8C;
        --blueprint-deep: #0E3450;
        --grid-line: #DAE5EE;
        --amber: #E2932F;
        --amber-deep: #B9741A;
        --ok: #2F8F5B;
        --danger: #C6432E;
        --line: #E3E8EC;
    }

    html, body, [class*="css"] { font-family: 'IBM Plex Sans', -apple-system, sans-serif; }
    .stApp { background: var(--paper); color: var(--ink); }
    .block-container { max-width: 1500px; padding-top: 1.6rem; padding-bottom: 3rem; }

    h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif; letter-spacing: -.01em; }

    /* ---------- Sidebar ---------- */
    [data-testid="stSidebar"] { background: var(--blueprint-deep); border-right: 1px solid rgba(255,255,255,.06); }
    [data-testid="stSidebar"] * { color: #EAF1F7; }
    [data-testid="stSidebar"] h2 { font-family: 'Space Grotesk', sans-serif; }
    [data-testid="stSidebar"] .stCaption { color: #8FA9BE !important; font-size: .72rem; letter-spacing: .07em; text-transform: uppercase; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label { color: #EAF1F7 !important; font-weight: 600 !important; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover { color: var(--amber) !important; }
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.1); }
    [data-testid="stSidebar"] strong { font-family: 'IBM Plex Mono', monospace; font-weight: 600; color: #FFFFFF; }

    /* ---------- Hero / title block (signature element) ---------- */
    .hero {
        position: relative;
        background: var(--panel);
        background-image:
            linear-gradient(var(--grid-line) 1px, transparent 1px),
            linear-gradient(90deg, var(--grid-line) 1px, transparent 1px);
        background-size: 22px 22px;
        border: 1px solid var(--line);
        border-radius: 4px;
        padding: 1.7rem 2rem;
        margin-bottom: 1.8rem;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        flex-wrap: wrap;
        gap: 1.2rem;
    }
    .hero::before, .hero::after {
        content: ""; position: absolute; width: 16px; height: 16px; border: 2px solid var(--amber);
    }
    .hero::before { top: -1px; left: -1px; border-right: none; border-bottom: none; }
    .hero::after { bottom: -1px; right: -1px; border-left: none; border-top: none; }
    .hero h1 { font-size: 2.05rem; margin: 0; color: var(--ink); }
    .hero p { color: var(--steel); margin: .5rem 0 0; font-size: .97rem; max-width: 44ch; }
    .hero .stamp {
        text-align: right; font-family: 'IBM Plex Mono', monospace; font-size: .72rem;
        color: var(--blueprint); line-height: 1.8; white-space: nowrap;
        border-left: 1px dashed var(--grid-line); padding-left: 1.2rem;
    }
    .hero .stamp b { color: var(--ink); }

    /* ---------- Section labels ---------- */
    .section-label {
        color: var(--blueprint); font-family: 'IBM Plex Mono', monospace; font-size: .74rem;
        font-weight: 600; letter-spacing: .1em; text-transform: uppercase;
        margin: 1.7rem 0 .55rem; display: flex; align-items: center; gap: .5rem;
    }
    .section-label::before { content: ""; width: 8px; height: 8px; background: var(--amber); flex-shrink: 0; }

    /* ---------- Buttons ---------- */
    .stButton > button {
        border-radius: 6px; font-weight: 600; min-height: 2.6rem; border: 1px solid var(--line);
        color: var(--ink); background: var(--panel);
    }
    .stButton > button:hover { border-color: var(--blueprint); color: var(--blueprint); }
    .stButton > button[kind="primary"] { background: var(--amber); border-color: var(--amber-deep); color: #1B2430; }
    .stButton > button[kind="primary"]:hover { background: var(--amber-deep); border-color: var(--amber-deep); color: #FFFFFF; }
    .stButton > button:disabled { opacity: .45; }

    /* ---------- Metrics ---------- */
    [data-testid="stMetric"] {
        background: var(--panel); border: 1px solid var(--line); border-top: 3px solid var(--blueprint);
        border-radius: 6px; padding: .7rem .9rem;
    }
    [data-testid="stMetricLabel"] { color: var(--steel); font-size: .74rem; text-transform: uppercase; letter-spacing: .07em; }
    [data-testid="stMetricValue"] { color: var(--ink); font-size: 1.45rem; font-family: 'IBM Plex Mono', monospace; font-weight: 600; }

    /* ---------- Form / inputs ---------- */
    [data-testid="stForm"] { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 1.2rem 1.4rem 0.6rem; }
    [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-testid="stSelectbox"] div[data-baseweb="select"] {
        border-radius: 6px !important;
    }
    [data-testid="stNumberInput"] input { font-family: 'IBM Plex Mono', monospace; }

    /* ---------- Table ---------- */
    .stDataFrame { border: 1px solid var(--line); border-radius: 6px; overflow: hidden; }
    .stDataFrame [data-testid="stElementToolbar"] { font-family: 'IBM Plex Mono', monospace; }

    /* ---------- Alerts ---------- */
    [data-testid="stAlert"] { border-radius: 6px; border: 1px solid var(--line); }

    /* ---------- Code / report block ---------- */
    [data-testid="stCodeBlock"] pre, [data-testid="stCodeBlock"] code {
        font-family: 'IBM Plex Mono', monospace !important; font-size: .82rem;
        background: var(--blueprint-deep) !important; color: #DCEBF5 !important; border-radius: 6px;
    }

    hr { border-color: var(--line); }
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

st.markdown(
    f"""
    <div class="hero">
        <div>
            <h1>Truck Load Optimizer</h1>
            <p>Build a practical loading plan, verify axle limits, and visualize the finished trailer.</p>
        </div>
        <div class="stamp">
            VEHICLE&nbsp;&nbsp;<b>{truck_name.upper()}</b><br>
            PAYLOAD LIMIT&nbsp;&nbsp;<b>{truck.legal_gross:,.0f} KG</b><br>
            BASIS&nbsp;&nbsp;<b>STATIC · LEVEL GROUND</b>
        </div>
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
