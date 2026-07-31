import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Optimizer",
    layout="wide"
)
st.title("5-Axle Load Optimizer")

class WebTruckOptimizer:
    def __init__(self, t_type):
        c_side = "Curtainsider"
        if c_side in t_type:
            self.trailer_length = 13.6
            self.trailer_width = 2.48
            self.max_cargo_wt = 24000
            self.empty_steer = 5200
            self.empty_drive = 2800
            self.empty_t1 = 2670
            self.empty_t2 = 2670
            self.empty_t3 = 2670
            self.empty_total = 16010
        else:
            self.trailer_length = 13.4
            self.trailer_width = 2.45
            self.max_cargo_wt = 22000
            self.empty_steer = 5400
            self.empty_drive = 3800
            self.empty_t1 = 2940
            self.empty_t2 = 2940
            self.empty_t3 = 2940
            self.empty_total = 18020

        self.kingpin_to_front = 1.6
        self.t2_pos = 11.6
        self.max_steer = 10000
        self.max_drive = 11500
        self.max_axle_trailer = 8000
        self.max_total_weight = 40000

    def generate_blueprint(
        self, mft, front_singles=2
    ):
        all_p = []
        for p in mft:
            for _ in range(int(p['qty'])):
                ow = p['width']
                ol = p['len']
                if p.get('auto_rotate', True):
                    mw = self.trailer_width * 100
                    if ol > ow and ol <= mw:
                        fw, fl = ol, ow
                    else:
                        fw, fl = ow, ol
                else:
                    fw, fl = ow, ol
                all_p.append({
                    'len': fl / 100.0,
                    'width': fw / 100.0,
                    'wt': p['wt'],
                    'name': p['name']
                })

        all_p.sort(
            key=lambda x: x['wt'],
            reverse=True
        )

        layout = []
        p_idx = 0
        total_p = len(all_p)
        row_idx = 0
        used_len = 0.0

        while p_idx < total_p:
            rem = total_p - p_idx
            next_len = 1.0
            if (used_len + next_len) > self.trailer_length:
                break
                
            if row_idx < front_singles:
                p1 = all_p[p_idx]
                layout.append({
                    'type': 'SINGLE_CENTER', 'p': [p1],
                    'len': p1['len'], 'wt': p1['wt']
                })
                p_idx += 1
                used_len += p1['len']
            else:
                if rem >= 2 and row_idx % 2 == 0:
                    p1 = all_p[p_idx]
                    p2 = all_p[p_idx+1]
                    cw = p1['width'] + p2['width']
                    if cw <= self.trailer_width:
                        layout.append({
                            'type': 'DOUBLE', 'p': [p1, p2],
                            'len': max(p1['len'], p2['len']),
                            'wt': p1['wt'] + p2['wt']
                        })
                        p_idx += 2
                        used_len += max(p1['len'], p2['len'])
                    else:
                        layout.append({
                            'type': 'SINGLE_CENTER', 'p': [p1],
                            'len': p1['len'], 'wt': p1['wt']
                        })
                        p_idx += 1
                        used_len += p1['len']
                else:
                    p1 = all_p[p_idx]
                    layout.append({
                        'type': 'SINGLE_CENTER', 'p': [p1],
                        'len': p1['len'], 'wt': p1['wt']
                    })
                    p_idx += 1
                    used_len += p1['len']
            row_idx += 1
            
        return layout

    def analyze(self, layout):
        tot_w = sum(r['wt'] for r in layout)
        kp_cargo_wt = 0.0
        t1_cargo_wt = 0.0
        t2_cargo_wt = 0.0
        t3_cargo_wt = 0.0

        c_dist = 0.0
        for r in layout:
            r_c = c_dist + (r['len'] / 2.0)
            rw = r['wt']
            wb = self.t2_pos - self.kingpin_to_front
            row_dist_kp = r_c - self.kingpin_to_front
            row_to_tridem = (rw * row_dist_kp) / wb
            row_to_kp = rw - row_to_tridem

            kp_cargo_wt += row_to_kp
            t1_cargo_wt += row_to_tridem * 0.34
            t2_cargo_wt += row_to_tridem * 0.33
            t3_cargo_wt += row_to_tridem * 0.33
            c_dist += r['len']

        drive_cargo = kp_cargo_wt * 0.85
        steer_cargo = kp_cargo_wt * 0.15

        return {
            'steer': round(self.empty_steer + steer_cargo),
            'drive': round(self.empty_drive + drive_cargo),
            't1': round(self.empty_t1 + t1_cargo_wt),
            't2': round(self.empty_t2 + t2_cargo_wt),
            't3': round(self.empty_t3 + t3_cargo_wt),
            'cargo_wt': tot_w,
            'gross_total': round(self.empty_total + tot_w),
            'cargo_len': round(c_dist, 2),
            'rear_gap': round(self.trailer_length - c_dist, 2)
        }

st.sidebar.header("1. Profile")
t_opts = ["Curtainsider", "Frigo"]
t_sel = st.sidebar.selectbox("Truck type", t_opts)
engine = WebTruckOptimizer(t_sel)

st.sidebar.header("2. Add Cargo")
if 'manifest' not in st.session_state:
    st.session_state.manifest = [{
        'name': 'Cargo', 'qty': 17,
        'width': 100, 'len': 120, 'wt': 1300,
        'auto_rotate': True
    }]

with st.sidebar.form("add_p_form"):
    p_name = st.text_input("Name", "Cargo")
    p_qty = st.number_input("Qty", min_value=1, value=1)
    p_width = st.number_input("W (cm)", min_value=10, value=100)
    p_len = st.number_input("L (cm)", min_value=10, value=120)
    p_wt = st.number_input("Wt (kg)", min_value=50, value=1300)
    p_rot = st.checkbox("Rotate", value=True)
    if st.form_submit_button("Add"):
        st.session_state.manifest.append({
            'name': p_name, 'qty': p_qty,
            'width': p_width, 'len': p_len,
            'wt': p_wt, 'auto_rotate': p_rot
        })

if st.sidebar.button("Clear"):
    st.session_state.manifest = []
    st.rerun()

c1, c2 = st.columns(2)
with c1:
    st.subheader("Manifest Editor")
    if len(st.session_state.manifest) == 0:
        st.info("Empty.")
    else:
        df = pd.DataFrame(st.session_state.manifest)
        ed_df = st.data_editor(
            df, column_config={
                "name": "Desc", "qty": "Qty",
                "width": "W (cm)", "len": "L (cm)",
                "wt": "Wt (kg)",
                "auto_rotate": st.column_config.CheckboxColumn("Rotate?")
            }, hide_index=True, use_container_width=True
        )
        st.session_state.manifest = ed_df.to_dict('records')

if len(st.session_state.manifest) > 0:
    singles_count = 1
    layout = engine.generate_blueprint(st.session_state.manifest, singles_count)
    res = engine.analyze(layout)

    while res['drive'] > engine.max_drive and singles_count < 8:
        singles_count += 1
        layout = engine.generate_blueprint(st.session_state.manifest, singles_count)
        res = engine.analyze(layout)

    with c2:
        st.subheader("5-Axle Scale Weight Report")
        if res['gross_total'] > engine.max_total_weight:
            st.error(f"OVERWEIGHT GROSS: {res['gross_total']:,} kg")
        else:
            st.success(f"Total Gross: {res['gross_total']:,} kg (LEGAL)")

        st.markdown("**Tractor Axles:**")
        if res['steer'] > engine.max_steer:
            st.error(f"Axle 1 (Steer): {res['steer']:,} kg")
        else:
            st.success(f"Axle 1 (Steer): {res['steer']:,} kg")

        if res['drive'] > engine.max_drive:
            st.error(f"Axle 2 (Drive): {res['drive']:,} kg")
        else:
            st.success(f"Axle 2 (Drive): {res['drive']:,} kg")

        st.markdown("**Trailer Axles:**")
        for idx, k in enumerate(['t1', 't2', 't3'], 3):
            v = res[k]
            if v > engine.max_axle_trailer:
                st.error(f"Axle {idx}: {v:,} kg")
            else:
                st.success(f"Axle {idx}: {v:,} kg")

    st.subheader("Real-Dimension Scaled Trailer Graph Map")
    st.info(f"Length Used: {res['cargo_len']}m / {engine.trailer_length}m")

    # --- NO-OVERFLOW GRID BLUEPRINT GENERATOR ---
    grid_rows = []
    current_y = 0.0
    
    for idx, r in enumerate(layout, 1):
        current_y += r['len']
        row_pos = f"{current_y:.1f} M"
        
        if r['type'] == 'DOUBLE':
            if len(r['p']) == 2:
                p1, p2 = r['p'], r['p']
                l_cell = f"[ {p1['name']} ({p1['wt']} kg) ]"
                r_cell = f"[ {p2['name']} ({p2['wt']} kg) ]"
            else:
                p1 = r['p']
                l_cell = f"[ {p1['name']} ({p1['wt']} kg) ]"
                r_cell = "[ VOID - LASH NEEDED ]"
        else:
            p1 = r['p']
            l_cell = f"--- [ {p1['name']} ({p1['wt']} kg) ] ---"
            r_cell = f"--- [ {p1['name']} ({p1['wt']} kg) ] ---"
            
        grid_rows.append({
            "Trailer Position": row_pos,
            "Left Side Column": l_cell,
            "Right Side Column": r_cell,
            "Total Row Weight (kg)": r['wt']
        })
        
    grid_df = pd.DataFrame(grid_rows)
    st.dataframe(
        grid_df,
        hide_index=True,
        use_container_width=True
    )
