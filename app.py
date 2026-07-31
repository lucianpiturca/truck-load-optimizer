import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Optimizer", 
    layout="wide"
)
st.title("Truck Load Optimizer")

class WebTruckOptimizer:
    def __init__(self, t_type):
        c_side = "Curtainsider"
        if c_side in t_type:
            self.trailer_length = 13.6
            self.trailer_width = 2.48  
            self.empty_steer = 4800
            self.empty_drive = 2200
            self.empty_tridem = 7000
            self.max_cargo_wt = 24000
        else:
            self.trailer_length = 13.4
            self.trailer_width = 2.45  
            self.empty_steer = 4900
            self.empty_drive = 2400
            self.empty_tridem = 7900  
            self.max_cargo_wt = 22000

        self.kingpin_to_front = 1.6
        self.wheelbase = 7.5
        self.max_drive = 11500  
        self.max_tridem = 24000  

    def generate_blueprint(self, mft):
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
        all_p.sort(key=lambda x: x['wt'], reverse=True)
        layout = []
        p_idx, row_idx = 0, 0
        total_p = len(all_p)
        while p_idx < total_p:
            rem = total_p - p_idx
            is_d1 = row_idx == 0 or row_idx == 3
            is_d2 = row_idx > 3 and row_idx % 2 == 1
            if is_d1 or is_d2 or rem == 2:
                if rem >= 2:
                    p1 = all_p[p_idx]
                    p2 = all_p[p_idx+1]
                    if (p1['width'] + p2['width']) <= self.trailer_width:
                        layout.append({
                            'type': 'DOUBLE', 'p': [p1, p2], 
                            'len': max(p1['len'], p2['len']), 
                            'wt': p1['wt'] + p2['wt']
                        })
                        p_idx += 2
                    else:
                        layout.append({
                            'type': 'SINGLE_CENTER', 'p': [p1], 
                            'len': p1['len'], 'wt': p1['wt']
                        })
                        p_idx += 1
                else:
                    p1 = all_p[p_idx]
                    layout.append({
                        'type': 'DOUBLE', 'p': [p1], 
                        'len': p1['len'], 'wt': p1['wt']
                    })
                    p_idx += 1
            else:
                p1 = all_p[p_idx]
                layout.append({
                    'type': 'SINGLE_CENTER', 'p': [p1], 
                    'len': p1['len'], 'wt': p1['wt']
                })
                p_idx += 1
            row_idx += 1
        return layout

    def analyze(self, layout):
        tot_w, w_dist, c_dist = 0, 0, 0.0
        for r in layout:
            r_c = c_dist + (r['len'] / 2.0)
            w_dist += r['wt'] * r_c
            tot_w += r['wt']
            c_dist += r['len']
        cog = w_dist / tot_w if tot_w > 0 else 0
        dist_kp = cog - self.kingpin_to_front
        w_tri = (tot_w * dist_kp) / self.wheelbase
        w_kp = tot_w - w_tri
        return {
            'steer': round(self.empty_steer + (w_kp * 0.25)),
            'drive': round(self.empty_drive + (w_kp * 0.75)),
            'tridem': round(self.empty_tridem + w_tri),
            'cargo_wt': tot_w, 'cargo_len': round(c_dist, 2),
            'rear_gap': round(self.trailer_length - c_dist, 2), 'cog': round(cog, 2)
        }

st.sidebar.header("Step 1")
t_opts = ["Curtainsider (24t)", "Frigo (22t)"]
t_sel = st.sidebar.selectbox("Truck", t_opts)
engine = WebTruckOptimizer(t_sel)

st.sidebar.header("Step 2")
if 'manifest' not in st.session_state:
    st.session_state.manifest = [{
        'name': 'Pallets', 'qty': 17, 'width': 100, 'len': 120, 'wt': 1300, 'auto_rotate': True
    }]

with st.sidebar.form("add_p_form"):
    p_name = st.text_input("Name", "Batch")
    p_qty = st.number_input("Qty", min_value=1, value=1)
    p_width = st.number_input("Width (cm)", min_value=10, value=100)
    p_len = st.number_input("Length (cm)", min_value=10, value=120)
    p_wt = st.number_input("Weight (kg)", min_value=50, value=1000)
    p_rot = st.checkbox("Auto Rotate", value=True)
    if st.form_submit_button("Add"):
        st.session_state.manifest.append({
            'name': p_name, 'qty': p_qty, 'width': p_width, 'len': p_len, 'wt': p_wt, 'auto_rotate': p_rot
        })

if st.sidebar.button("Clear"):
    st.session_state.manifest = []
    st.rerun()

c1, c2 = st.columns(2)
with c1:
    st.subheader("Manifest")
    if len(st.session_state.manifest) == 0:
        st.info("Empty.")
    else:
        df = pd.DataFrame(st.session_state.manifest)
        ed_df = st.data_editor(
            df, column_config={
                "name": "Desc", "qty": "Qty", "width": "W", "len": "L", "wt": "Wt",
                "auto_rotate": st.column_config.CheckboxColumn("Rotate")
            }, hide_index=True, use_container_width=True
        )
        st.session_state.manifest = ed_df.to_dict('records')

if len(st.session_state.manifest) > 0:
    layout = engine.generate_blueprint(st.session_state.manifest)
    res = engine.analyze(layout)
    with c2:
        st.subheader("Weights")
        st.metric("Total", f"{res['cargo_wt']:,} kg")
        st.metric("Drive", f"{res['drive']:,} kg")
        st.metric("Trailer", f"{res['tridem']:,} kg")

    st.subheader("Trailer Map")
    sy, sx = 60, 160
    cw = int(engine.trailer_width * sx)
    ch = int(engine.trailer_length * sy)
    
    st.markdown(f"""
        <style>
        .t-bed {{ position: relative; width: {cw}px; height: {ch}px; border: 4px solid #111; background: #fff; margin: 0 auto; }}
        .g-ln {{ position: absolute; left: 0; width: 100%; border-top: 1px dashed #ccc; }}
        .g-lb {{ position: absolute; left: -30px; color: #555; font-size: 10px; font-weight: bold; }}
        .p-un {{ position: absolute; background: #1d4ed8; color: white; border: 1px solid #000; border-radius: 2px; display: flex; flex-direction: column; justify-content: center; align-items: center; font-size: 9px; font-weight: bold; overflow: hidden; }}
        .p-sng {{ background: #0284c7; }}
        </style>
    """, unsafe_allow_html=True)

    h = "<div>FRONT</div>"
    h += f"<div class='t-bed'>"
    for m in range(1, int(engine.trailer_length) + 1):
        tp = int(m * sy)
        h += f"<div class='g-ln' style='top:{tp}px;'><span class='g-lb'>{m}M</span></div>"

    cy = 0.0
    for r in layout:
        rl = r['len']
        bh = int(rl * sy)
        pt = int(cy * sy)
        if r['type'] == 'DOUBLE':
            if len(r['p']) == 2:
                p1, p2 = r['p'][0], r['p'][1]
                w1 = int(p1['width'] * sx)
                w2 = int(p2['width'] * sx)
                h += f"<div class='p-un' style='left:0;top:{pt}px;width:{w1}px;height:{bh}px;'>{p1['name']}<br>{p1['wt']}k</div>"
                h += f"<div class='p-un' style='right:0;top:{pt}px;width:{w2}px;height:{bh}px;'>{p2['name']}<br>{p2['wt']}k</div>"
            else:
                p1 = r['p'][0]
                w1 = int(p1['width'] * sx)
                h += f"<div class='p-un' style='left:0;top:{pt}px;width:{w1}px;height:{bh}px;'>{p1['name']}<br>{p1['wt']}k</div>"
        else:
            p1 = r['p'][0]
            w1 = int(p1['width'] * sx)
            pl = int((cw - w1) / 2)
            h += f"<div class='p-un p-sng' style='left:{pl}px;top:{pt}px;width:{w1}px;height:{bh}px;'>{p1['name']}<br>{p1['wt']}k</div>"
        cy += rl
    h += "</div><div>REAR</div>"
    st.markdown(h, unsafe_allow_html=True)
