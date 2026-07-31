import streamlit as st
import pandas as pd

# --- STYLING & PAGE INITIALIZATION ---
st.set_page_config(page_title="Truck Axle Load Optimizer", layout="wide", page_icon="🚛")
st.title("🚛 Truck Axle Load & Placement Optimizer")
st.markdown("Calculate gap-free, anti-toppling layouts for mixed cargo to keep your axles 100% legal.")

# --- ENGINE: CALCULATIONS & RIGID PHYSICAL MODEL ---
class WebTruckOptimizer:
    def __init__(self, truck_type):
        # All standard European semi-trailer setups (4x2 tractor + 3-axle trailer)
        self.trailer_length = 13.6
        self.kingpin_to_front = 1.6
        self.wheelbase = 7.5
        
        # Base tare weights for standard configurations
        if truck_type == "European Curtainsider (Max 24t Cargo)":
            self.empty_steer = 4800
            self.empty_drive = 2200
            self.empty_tridem = 7000
            self.max_cargo_wt = 24000
        else:  # European Frigo Truck (Max 22t Cargo)
            self.empty_steer = 4900
            self.empty_drive = 2400
            self.empty_tridem = 7900  # Heavier cooling units
            self.max_cargo_wt = 22000

        self.max_drive = 11500  # Legal EU limit for drive axle
        self.max_tridem = 24000  # Legal EU limit for triple axle group

    def generate_blueprint(self, manifest):
        all_pallets = []
        for p in manifest:
            for _ in range(p['qty']):
                all_pallets.append({'len': p['len']/100.0, 'wt': p['wt'], 'name': p['name']})
        
        # Heaviest first for stability anchoring
        all_pallets.sort(key=lambda x: x['wt'], reverse=True)
        
        layout = []
        p_idx = 0
        total_p = len(all_pallets)
        row_idx = 0
        
        while p_idx < total_p:
            remaining = total_p - p_idx
            
            # Target layout logic built across our testing (forcing 2-1-1-2 front + alternation)
            if row_idx == 0 or row_idx == 3 or (row_idx > 3 and row_idx % 2 == 1) or remaining == 2:
                if remaining >= 2:
                    layout.append({
                        'type': 'DOUBLE', 
                        'p': [all_pallets[p_idx], all_pallets[p_idx+1]], 
                        'len': max(all_pallets[p_idx]['len'], all_pallets[p_idx+1]['len']), 
                        'wt': all_pallets[p_idx]['wt'] + all_pallets[p_idx+1]['wt']
                    })
                    p_idx += 2
                else:
                    layout.append({
                        'type': 'DOUBLE', 
                        'p': [all_pallets[p_idx]], 
                        'len': all_pallets[p_idx]['len'], 
                        'wt': all_pallets[p_idx]['wt']
                    })
                    p_idx += 1
            else:
                layout.append({
                    'type': 'SINGLE_CENTER', 
                    'p': [all_pallets[p_idx]], 
                    'len': all_pallets[p_idx]['len'], 
                    'wt': all_pallets[p_idx]['wt']
                })
                p_idx += 1
            row_idx += 1
            
        return layout

    def analyze(self, layout):
        total_wt = 0
        weighted_dist = 0
        curr_dist = 0.0
        for row in layout:
            row_center = curr_dist + (row['len'] / 2.0)
            weighted_dist += row['wt'] * row_center
            total_wt += row['wt']
            curr_dist += row['len']
            
        cog = weighted_dist / total_wt if total_wt > 0 else 0
        cargo_dist_kp = cog - self.kingpin_to_front
        wt_tridem = (total_wt * cargo_dist_kp) / self.wheelbase
        wt_kp = total_wt - wt_tridem
        
        return {
            'steer': round(self.empty_steer + (wt_kp * 0.25)),
            'drive': round(self.empty_drive + (wt_kp * 0.75)),
            'tridem': round(self.empty_tridem + wt_tridem),
            'cargo_wt': total_wt,
            'cargo_len': round(curr_dist, 2),
            'rear_gap': round(self.trailer_length - curr_dist, 2),
            'cog': round(cog, 2)
        }

# --- SIDEBAR CONTROL PANEL (USER INTERFACE) ---
st.sidebar.header("Step 1: Vehicle Configuration")
truck_selection = st.sidebar.selectbox(
    "Select Truck Profile", 
    ["European Curtainsider (Max 24t Cargo)", "European Frigo Truck (Max 22t Cargo)"]
)
engine = WebTruckOptimizer(truck_selection)

st.sidebar.header("Step 2: Add Pallet Batches")
if 'manifest' not in st.session_state:
    st.session_state.manifest = [{'name': 'Heavy Box Pallets', 'qty': 17, 'len': 100, 'wt': 1300}]

with st.sidebar.form("add_pallet_form"):
    p_name = st.text_input("Cargo Description / Name", "Standard Industrial Pallets")
    p_qty = st.number_input("Quantity of Pallets", min_value=1, value=5)
    p_len = st.number_input("Pallet Length/Depth (cm along truck)", min_value=10, value=100, step=10)
    p_wt = st.number_input("Weight per Pallet (kg)", min_value=50, value=1200, step=50)
    submitted = st.form_submit_button("➕ Add Batch to Truck")
    if submitted:
        st.session_state.manifest.append({'name': p_name, 'qty': p_qty, 'len': p_len, 'wt': p_wt})

if st.sidebar.button("🗑️ Clear Entire Manifest"):
    st.session_state.manifest = []
    st.rerun()

# --- MAIN SCREEN INTERFACE DISPLAY ---
col1, col2 = st.columns(2)  # FIXED HERE: SPECIFIED COLUMN COUNT

with col1:
    st.subheader("📋 Current Truck Manifest")
    if len(st.session_state.manifest) == 0:
        st.info("The truck is completely empty. Add some pallet batches via the sidebar panel.")
    else:
        df = pd.DataFrame(st.session_state.manifest)
        df.columns = ["Description", "Quantity", "Depth (cm)", "Unit Weight (kg)"]
        st.dataframe(df, use_container_width=True)

if len(st.session_state.manifest) > 0:
    layout = engine.generate_blueprint(st.session_state.manifest)
    res = engine.analyze(layout)
    
    with col2:
        st.subheader("⚖️ Live Axle Weight Scale Status")
        
        # Total Cargo Capacity Bar
        cargo_pct = res['cargo_wt'] / engine.max_cargo_wt
        if cargo_pct > 1.0:
            st.error(f"❌ OVER TOTAL CARGO CAPACITY! {res['cargo_wt']:,} kg / Max Allowed: {engine.max_cargo_wt:,} kg")
        else:
            st.success(f"📦 Total Cargo Load: {res['cargo_wt']:,} kg / Max Allowed: {engine.max_cargo_wt:,} kg")
        st.progress(min(cargo_pct, 1.0))
        
        # Display Drive with Adaptive Color Alerts
        drive_pct = res['drive'] / engine.max_drive
        if drive_pct > 1.0:
            st.error(f"🚨 OVERLOAD ON DRIVE AXLE! {res['drive']:,} kg / Max Allowed: {engine.max_drive:,} kg")
        elif drive_pct > 0.95:
            st.warning(f"⚠️ DRIVE AXLE CLOSE TO LIMIT: {res['drive']:,} kg / Max Allowed: {engine.max_drive:,} kg")
        else:
            st.success(f"✅ Drive Axle Legal: {res['drive']:,} kg / Max Allowed: {engine.max_drive:,} kg")
        st.progress(min(drive_pct, 1.0))

        # Display Trailer Tridem
        tridem_pct = res['tridem'] / engine.max_tridem
        if tridem_pct > 1.0:
            st.error(f"🚨 OVERLOAD ON TRAILER TRIDEM! {res['tridem']:,} kg / Max Allowed: {engine.max_tridem:,} kg")
        else:
            st.success(f"✅ Trailer Axles Legal: {res['tridem']:,} kg / Max Allowed: {engine.max_tridem:,} kg")
        st.progress(min(tridem_pct, 1.0))

    st.subheader("🗺️ Live Loading Map Layout (Front to Rear Doors)")
    st.info(f"Total Length Used: **{res['cargo_len']} m** | Total Weight: **{res['cargo_wt']:,} kg** | Empty Rear Space: **{res['rear_gap']} m**")
    
    # Render interactive blueprint grids
    st.markdown("📂 **[FRONT HEADBOARD]**")
    for r_idx, row in enumerate(layout, 1):
        if row['type'] == 'DOUBLE':
            if len(row['p']) == 2:
                label = f"Row {r_idx:02d} [Double]: [ {row['p'][0]['name']} | {row['p'][0]['wt']}kg ] 🔀 [ {row['p'][1]['name']} | {row['p'][1]['wt']}kg ]"
                st.code(label, language="text")
            else:
                label = f"Row {r_idx:02d} [Double-Blocked]: [ {row['p'][0]['name']} | {row['p'][0]['wt']}kg ] 🔀 [ EMPTY SPACE ]"
                st.code(label, language="text")
        else:
            label = f"Row {r_idx:02d} [Single Center]:                🔹 [ {row['p'][0]['name']} | {row['p'][0]['wt']}kg ] 🔹"
            st.code(label, language="text")
    st.markdown("🚪 **[REAR TRAILER DOORS]**")
