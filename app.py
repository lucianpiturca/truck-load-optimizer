import streamlit as st
import pandas as pd

# --- STYLING & PAGE INITIALIZATION ---
st.set_page_config(page_title="Truck Axle Load Optimizer", layout="wide", page_icon="🚛")
st.title("🚛 Truck Axle Load & Placement Optimizer")
st.markdown("Calculate gap-free layouts for mixed cargo sizes while strictly enforcing physical width constraints, orientation rules, and legal axle weights.")

# --- ENGINE: CALCULATIONS & RIGID PHYSICAL MODEL ---
class WebTruckOptimizer:
    def __init__(self, truck_type):
        self.trailer_length = 13.6
        self.trailer_width = 2.45  # 245 cm standard interior width
        self.kingpin_to_front = 1.6
        self.wheelbase = 7.5
        
        if truck_type == "European Curtainsider (Max 24t Cargo)":
            self.empty_steer = 4800
            self.empty_drive = 2200
            self.empty_tridem = 7000
            self.max_cargo_wt = 24000
        else:  # European Frigo Truck (Max 22t Cargo)
            self.empty_steer = 4900
            self.empty_drive = 2400
            self.empty_tridem = 7900  
            self.max_cargo_wt = 22000

        self.max_drive = 11500  
        self.max_tridem = 24000  

    def generate_blueprint(self, manifest):
        all_pallets = []
        for p in manifest:
            for _ in range(int(p['qty'])):
                orig_w = p['width']
                orig_l = p['len']
                
                # Check rotation flags
                if p.get('auto_rotate', True):
                    if orig_l > orig_w and orig_l <= (self.trailer_width * 100):
                        fit_width = orig_l
                        fit_length = orig_w
                    else:
                        fit_width = orig_w
                        fit_length = orig_l
                else:
                    fit_width = orig_w
                    fit_length = orig_l

                all_pallets.append({
                    'len': fit_length / 100.0, 
                    'width': fit_width, 
                    'wt': p['wt'], 
                    'name': p['name']
                })
        
        all_pallets.sort(key=lambda x: x['wt'], reverse=True)
        
        layout = []
        p_idx = 0
        total_p = len(all_pallets)
        row_idx = 0
        
        while p_idx < total_p:
            remaining = total_p - p_idx
            
            if row_idx == 0 or row_idx == 3 or (row_idx > 3 and row_idx % 2 == 1) or remaining == 2:
                if remaining >= 2:
                    p1 = all_pallets[p_idx]
                    p2 = all_pallets[p_idx+1]
                    
                    if (p1['width'] + p2['width']) <= (self.trailer_width * 100):
                        layout.append({
                            'type': 'DOUBLE', 
                            'p': [p1, p2], 
                            'len': max(p1['len'], p2['len']), 
                            'wt': p1['wt'] + p2['wt']
                        })
                        p_idx += 2
                    else:
                        layout.append({
                            'type': 'SINGLE_CENTER', 
                            'p': [p1], 
                            'len': p1['len'], 
                            'wt': p1['wt'],
                            'note': "Width exceeds trailer limit! Try enabling rotation."
                        })
                        p_idx += 1
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

# --- SIDEBAR CONTROL PANEL ---
st.sidebar.header("Step 1: Vehicle Configuration")
truck_selection = st.sidebar.selectbox(
    "Select Truck Profile", 
    ["European Curtainsider (Max 24t Cargo)", "European Frigo Truck (Max 22t Cargo)"]
)
engine = WebTruckOptimizer(truck_selection)

st.sidebar.header("Step 2: Add Pallet Batches")
if 'manifest' not in st.session_state:
    st.session_state.manifest = [
        {'name': 'Heavy Box Pallets', 'qty': 17, 'width': 100, 'len': 120, 'wt': 1300, 'auto_rotate': True}
    ]

with st.sidebar.form("add_pallet_form"):
    p_name = st.text_input("Cargo Description / Name", "Mixed Pallet Batch")
    p_qty = st.number_input("Quantity of Pallets", min_value=1, value=1)
    p_width = st.number_input("Pallet Width (cm)", min_value=10, max_value=245, value=100, step=5)
    p_len = st.number_input("Pallet Length/Depth (cm)", min_value=10, value=120, step=10)
    p_wt = st.number_input("Weight per Pallet (kg)", min_value=50, value=1000, step=50)
    p_rotate = st.checkbox("Allow Automatic Rotation for Best Fit", value=True)
    submitted = st.form_submit_button("➕ Add Batch to Truck")
    if submitted:
        st.session_state.manifest.append({
            'name': p_name, 'qty': p_qty, 'width': p_width, 'len': p_len, 'wt': p_wt, 'auto_rotate': p_rotate
        })

if st.sidebar.button("🗑️ Clear Entire Manifest"):
    st.session_state.manifest = []
    st.rerun()

# --- MAIN DASHBOARD INTERFACE DISPLAY ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Current Truck Manifest")
    if len(st.session_state.manifest) == 0:
        st.info("The truck is completely empty.")
    else:
        df_base = pd.DataFrame(st.session_state.manifest)
        edited_df = st.data_editor(
            df_base,
            column_config={
                "name": "Description",
                "qty": "Quantity",
                "width": "Width (cm)",
                "len": "Length (cm)",
                "wt": "Weight (kg)",
                "auto_rotate": st.column_config.CheckboxColumn("Auto Rotate?", default=True)
            },
            hide_index=True,
            use_container_width=True
        )
        st.session_state.manifest = edited_df.to_dict('records')

if len(st.session_state.manifest) > 0:
    layout = engine.generate_blueprint(st.session_state.manifest)
    res = engine.analyze(layout)
    
    with col2:
        st.subheader("⚖️ Live Axle Weight Scale Status")
        cargo_pct = res['cargo_wt'] / engine.max_cargo_wt
        if cargo_pct > 1.0:
            st.error(f"❌ OVER TOTAL CARGO CAPACITY! {res['cargo_wt']:,} kg / Max: {engine.max_cargo_wt:,} kg")
        else:
            st.success(f"📦 Total Cargo Load: {res['cargo_wt']:,} kg / Max: {engine.max_cargo_wt:,} kg")
        st.progress(min(cargo_pct, 1.0))
        
        drive_pct = res['drive'] / engine.max_drive
        if drive_pct > 1.0:
            st.error(f"🚨 OVERLOAD ON DRIVE AXLE! {res['drive']:,} kg / Max: {engine.max_drive:,} kg")
        elif drive_pct > 0.95:
            st.warning(f"⚠️ DRIVE AXLE CLOSE TO LIMIT: {res['drive']:,} kg / Max: {engine.max_drive:,} kg")
        else:
            st.success(f"✅ Drive Axle Legal: {res['drive']:,} kg / Max: {engine.max_drive:,} kg")
        st.progress(min(drive_pct, 1.0))

        tridem_pct = res['tridem'] / engine.max_tridem
        if tridem_pct > 1.0:
            st.error(f"🚨 OVERLOAD ON TRAILER TRIDEM! {res['tridem']:,} kg / Max: {engine.max_tridem:,} kg")
        else:
            st.success(f"✅ Trailer Axles Legal: {res['tridem']:,} kg / Max: {engine.max_tridem:,} kg")
        st.progress(min(tridem_pct, 1.0))

    st.subheader("🗺️ Live Loading Map Layout (with 1-Meter Incremental Grid Lines)")
    st.info(f"Total Cargo Length: **{res['cargo_len']} m** | Empty Rear Space: **{res['rear_gap']} m** | Width: **2.45 m**")
    
    st.markdown("📂 **==================== [ FRONT HEADBOARD ] ====================**")
    
    accumulated_length = 0.0
    next_meter_marker = 1.0
    
    for r_idx, row in enumerate(layout, 1):
        row_len = row['len']
        row_start = accumulated_length
        row_end = accumulated_length + row_len
        
        while next_meter_marker <= row_end and next_meter_marker <= 13.6:
            if next_meter_marker <= row_start:
                st.markdown(f"📐 --- **{next_meter_marker:.0f} METER LINE** ---")
            elif row_start < next_meter_marker < row_end:
                st.markdown(f"📐 --- **{next_meter_marker:.0f} METER LINE (Crosses Row {r_idx:02d})** ---")
            next_meter_marker += 1.0
            
        note_str = row.get('note', '')
        
        if row['type'] == 'DOUBLE':
            if len(row['p']) == 2:
                p1, p2 = row['p'][0], row['p'][1]
label = f"Row {r_idx:02d} [Double - {row_len100:.0f}cm Deep]: [ {p1['name']} | W:{p1['width']}cm | {p1['wt']}kg ] 🔀 [ {p2['name']} | W:{p2['width']}cm | {p2['wt']}kg ]"st.code(label, language="text")else:p1 = row['p'][0]label = f"Row {r_idx:02d} [Single - {row_len100:.0f}cm Deep]: [ {p1['name']} | W:{p1['width']}cm | {p1['wt']}kg ] 🔀 [ BLOCKING REQD ]"st.code(label, language="text")else:p1 = row['p'][0]warn_decorator = " ⚠️ " if note_str else ""label = f"Row {r_idx:02d} [Center Single - {row_len*100:.0f}cm Deep]:          🔹 [ {p1['name']} | W:{p1['width']}cm | {p1['wt']}kg ] 🔹 {warn_decorator}{note_str}"st.code(label, language="text")accumulated_length = row_endwhile next_meter_marker <= 13.0:st.markdown(f"📐 --- {next_meter_marker:.0f} METER LINE (EMPTY ZONE) ---")next_meter_marker += 1.0st.markdown("🚪 ==================== [ REAR TRAILER DOORS ] ====================")