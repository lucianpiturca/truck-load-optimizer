import streamlit as st
import pandas as pd

# --- STYLING & PAGE INITIALIZATION ---
st.set_page_config(
    page_title="Optimizer", 
    layout="wide"
)
st.title("Truck Load Optimizer")
st.markdown("Calculate gap-free layouts.")

# --- ENGINE ---
class WebTruckOptimizer:
    def __init__(self, truck_type):
        self.trailer_length = 13.6
        self.trailer_width = 2.45  
        self.kingpin_to_front = 1.6
        self.wheelbase = 7.5
        
        c_side = "Curtainsider"
        if c_side in truck_type:
            self.empty_steer = 4800
            self.empty_drive = 2200
            self.empty_tridem = 7000
            self.max_cargo_wt = 24000
        else:  
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
                
                if p.get('auto_rotate', True):
                    max_w = self.trailer_width * 100
                    if orig_l > orig_w and orig_l <= max_w:
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
        
        all_pallets.sort(
            key=lambda x: x['wt'], 
            reverse=True
        )
        
        layout = []
        p_idx = 0
        total_p = len(all_pallets)
        row_idx = 0
        
        while p_idx < total_p:
            remaining = total_p - p_idx
            
            is_d1 = row_idx == 0 or row_idx == 3
            is_d2 = row_idx > 3 and row_idx % 2 == 1
            if is_d1 or is_d2 or remaining == 2:
                if remaining >= 2:
                    p1 = all_pallets[p_idx]
                    p2 = all_pallets[p_idx+1]
                    max_w = self.trailer_width * 100
                    if (p1['width'] + p2['width']) <= max_w:
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
                            'note': "Width limit exceeded!"
                        })
                        p_idx += 1
                else:
                    p1 = all_pallets[p_idx]
                    layout.append({
                        'type': 'DOUBLE', 
                        'p': [p1], 
                        'len': p1['len'], 
                        'wt': p1['wt']
                    })
                    p_idx += 1
            else:
                p1 = all_pallets[p_idx]
                layout.append({
                    'type': 'SINGLE_CENTER', 
                    'p': [p1], 
                    'len': p1['len'], 
                    'wt': p1['wt']
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
            
        if total_wt > 0:
            cog = weighted_dist / total_wt
        else:
            cog = 0
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

# --- CONTROL PANEL ---
st.sidebar.header("Step 1: Profile")
t_opts = ["Curtainsider (24t)", "Frigo Truck (22t)"]
truck_selection = st.sidebar.selectbox("Truck Type", t_opts)
engine = WebTruckOptimizer(truck_selection)

st.sidebar.header("Step 2: Add Batches")
if 'manifest' not in st.session_state:
    st.session_state.manifest = [{
        'name': 'Heavy Pallets', 'qty': 17, 
        'width': 100, 'len': 120, 'wt': 1300, 
        'auto_rotate': True
    }]

with st.sidebar.form("add_pallet_form"):
    p_name = st.text_input("Name", "Batch")
    p_qty = st.number_input("Qty", min_value=1, value=1)
    p_width = st.number_input("Width (cm)", min_value=10, value=100)
    p_len = st.number_input("Length (cm)", min_value=10, value=120)
    p_wt = st.number_input("Weight (kg)", min_value=50, value=1000)
    p_rotate = st.checkbox("Auto Rotate", value=True)
    submitted = st.form_submit_button("Add")
    if submitted:
        st.session_state.manifest.append({
            'name': p_name, 'qty': p_qty, 'width': p_width, 
            'len': p_len, 'wt': p_wt, 'auto_rotate': p_rotate
        })

if st.sidebar.button("Clear Manifest"):
    st.session_state.manifest = []
    st.rerun()

# --- MAIN INTERFACE DISPLAY ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Manifest")
    if len(st.session_state.manifest) == 0:
        st.info("Truck empty.")
    else:
        df_base = pd.DataFrame(st.session_state.manifest)
        edited_df = st.data_editor(
            df_base,
            column_config={
                "name": "Desc", "qty": "Qty",
                "width": "W (cm)", "len": "L (cm)", "wt": "Wt (kg)",
                "auto_rotate": st.column_config.CheckboxColumn("Rotate?")
            },
            hide_index=True,
            use_container_width=True
        )
        st.session_state.manifest = edited_df.to_dict('records')

if len(st.session_state.manifest) > 0:
    layout = engine.generate_blueprint(st.session_state.manifest)
    res = engine.analyze(layout)
    
    with col2:
        st.subheader("Scale Weights")
        st.metric("Total Load", f"{res['cargo_wt']:,} kg")
        st.metric("Drive Axle", f"{res['drive']:,} kg")
        st.metric("Trailer Axles", f"{res['tridem']:,} kg")

    st.subheader("Loading Map Layout")
    st.markdown("--- [ FRONT HEADBOARD ] ---")
    
    accumulated_length = 0.0
    next_meter_marker = 1.0
    
    for r_idx, row in enumerate(layout, 1):
        row_len = row['len']
        row_start = accumulated_length
        row_end = accumulated_length + row_len
        
        while next_meter_marker <= row_end and next_meter_marker <= 13.6:
            if next_meter_marker <= row_start:
                st.markdown(f"METER LINE: {next_meter_marker:.0f} M")
            elif row_start < next_meter_marker < row_end:
                st.markdown(f"METER LINE: {next_meter_marker:.0f} M (Row {r_idx})")
            next_meter_marker += 1.0
            
        note_str = row.get('note', '')
        
        if row['type'] == 'DOUBLE':
            if len(row['p']) == 2:
                p1, p2 = row['p'][0], row['p'][1]
                lbl = f"Row {r_idx:02d} [Double - {row_len*100:.0f}cm]: "
                lbl += f"[{p1['name']}|W:{p1['width']}cm|{p1['wt']}kg] + "
                lbl += f"[{p2['name']}|W:{p2['width']}cm|{p2['wt']}kg]"
                st.code(lbl, language="text")
            else:
                p1 = row['p'][0]
                lbl = f"Row {r_idx:02d} [Double]: "
                lbl += f"[{p1['name']}|W:{p1['width']}cm|{p1['wt']}kg] + "
                lbl += "[BLOCKING REQD]"
                st.code(lbl, language="text")
        else:
            p1 = row['p'][0]
            warn_decorator = " WARN: " if note_str else ""
            lbl = f"Row {r_idx:02d} [Center Single]: "
            lbl += f"--- [{p1['name']}|W:{p1['width']}cm|{p1['wt']}kg] ---"
            lbl += f"{warn_decorator}{note_str}"
            st.code(lbl, language="text")
            
        accumulated_length = row_end

    while next_meter_marker <= 13.0:
        st.markdown(f"METER LINE: {next_meter_marker:.0f} M (EMPTY)")
        next_meter_marker += 1.0
        
    st.markdown("--- [ REAR TRAILER DOORS ] ---")
