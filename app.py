import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Optimizer 5 Axe", 
    layout="wide"
)
st.title("Optimizator Incarcare 5 Axe (Romania/EU)")

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
        self.wheelbase = 7.5
        self.t1_pos = 10.3
        self.t2_pos = 11.6
        self.t3_pos = 12.9
        
        self.max_steer = 10000
        self.max_drive = 11500
        self.max_axle_trailer = 8000
        self.max_total_weight = 40000

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
        
        pattern = [2, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 2]
        layout = []
        p_idx = 0
        total_p = len(all_p)
        
        for step in pattern:
            if p_idx >= total_p:
                break
            count = min(step, total_p - p_idx)
            
            if count == 2:
                p1 = all_p[p_idx]
                p2 = all_p[p_idx+1]
                layout.append({
                    'type': 'DOUBLE', 'p': [p1, p2], 
                    'len': max(p1['len'], p2['len']), 
                    'wt': p1['wt'] + p2['wt']
                })
                p_idx += 2
            elif count == 1:
                p1 = all_p[p_idx]
                layout.append({
                    'type': 'SINGLE_CENTER', 'p': [p1], 
                    'len': p1['len'], 'wt': p1['wt']
                })
                p_idx += 1
                
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
            
        drive_cargo = kp_cargo_wt * 0.81
        steer_cargo = kp_cargo_wt * 0.19
        
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

st.sidebar.header("1. Tip Vehicul")
t_opts = ["Curtainsider (16t Tara / 24t Cargo)", "Frigo (18t Tara / 22t Cargo)"]
t_sel = st.sidebar.selectbox("Configuratie Camion", t_opts)
engine = WebTruckOptimizer(t_sel)

st.sidebar.header("2. Adauga Paleti")
if 'manifest' not in st.session_state:
    st.session_state.manifest = [{
        'name': 'Palet Box', 'qty': 17, 'width': 100, 'len': 120, 'wt': 1300, 'auto_rotate': True
    }]

with st.sidebar.form("add_p_form"):
    p_name = st.text_input("Denumire Marfa", "Palet Box")
    p_qty = st.number_input("Cantitate (Buc)", min_value=1, value=1)
    p_width = st.number_input("Latime (cm)", min_value=10, value=100)
    p_len = st.number_input("Lungime (cm)", min_value=10, value=120)
    p_wt = st.number_input("Greutate Palet (kg)", min_value=50, value=1300)
    p_rot = st.checkbox("Permite Auto-Rotire", value=True)
    if st.form_submit_button("Adauga"):
        st.session_state.manifest.append({
            'name': p_name, 'qty': p_qty, 'width': p_width, 'len': p_len, 'wt': p_wt, 'auto_rotate': p_rot
        })

if st.sidebar.button("Goleste Camion"):
    st.session_state.manifest = []
    st.rerun()

c1, c2 = st.columns(2)
with c1:
    st.subheader("Manifest Curent Incarcare")
    if len(st.session_state.manifest) == 0:
        st.info("Camionul este gol.")
    else:
        df = pd.DataFrame(st.session_state.manifest)
        ed_df = st.data_editor(
            df, column_config={
                "name": "Descriere", "qty": "Buc", "width": "L (cm)", "len": "H (cm)", "wt": "G (kg)",
                "auto_rotate": st.column_config.CheckboxColumn("Rotire")
            }, hide_index=True, use_container_width=True
        )
        st.session_state.manifest = ed_df.to_dict('records')

if len(st.session_state.manifest) > 0:
    layout = engine.generate_blueprint(st.session_state.manifest)
    res = engine.analyze(layout)
    
    with c2:
        st.subheader("Cantar electronic (Raport Cele 5 Axe)")
        if res['gross_total'] > engine.max_total_weight:
            st.error(f"DEPASED LIMIT: {res['gross_total']:,} kg / Max: {engine.max_total_weight:,} kg")
        else:
            st.success(f"Masa Totala: {res['gross_total']:,} kg (LEGAL)")
            
        st.markdown("**Cap Tractor (Axe 1 - 2):**")
        if res['steer'] > engine.max_steer:
            st.error(f"Axa 1 (Directie): {res['steer']:,} kg")
        else:
            st.success(f"Axa 1 (Directie): {res['steer']:,} kg")
            
        if res['drive'] > engine.max_drive:
            st.error(f"Axa 2 (Tractiune): {res['drive']:,} kg")
        else:
            st.success(f"Axa 2 (Tractiune): {res['drive']:,} kg")
            
        st.markdown("**Semiremorca (Axe 3 - 4 - 5):**")
        for idx, axle_key in enumerate(['t1', 't2', 't3'], 3):
            val = res[axle_key]
            if val > engine.max_axle_trailer:
                st.error(f"Axa {idx}: {val:,} kg")
            else:
                st.success(f"Axa {idx}: {val:,} kg")

    st.subheader("Harta Scalata la Dimensiuni Reale")
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

    # Izolare sigura anti-scurgere text prin variabile de separare
    LT = "<"
    GT = ">"
    
    h = "<div>PERETE FRONTAL (CALE)</div>"
    h += LT + f"div class='t-bed'" + GT
    for m in range(1, int(engine.trailer_length) + 1):
        tp = int(m * sy)
        h += LT + f"div class='g-ln' style='top:{tp}px;'" + GT
        h += LT + f"span class='g-lb'" + GT + f"{m}M" + LT + "/span" + GT
        h += LT + "/div" + GT

    cy = 0.0
    for r in layout:
        rl = r['len']
        bh = int(rl * sy)
        pt = int(cy * sy)
        if r['type'] == 'DOUBLE':
            if len(r['p']) == 2:
                p1 = r['p'][0]
                p2 = r['p'][1]
                w1 = int(p1['width'] * sx)
                w2 = int(p2['width'] * sx)
                h += LT + f"div class='p-un' style='left:0;top:{pt}px;width:{w1}px;height:{bh}px;'" + GT + f"{p1['name']}" + LT + "br" + GT + f"{p1['wt']}k" + LT + "/div" + GT
                h += LT + f"div class='p-un' style='right:0;top:{pt}px;width:{w2}px;height:{bh}px;'" + GT + f"{p2['name']}" + LT + "br" + GT + f"{p2['wt']}k" + LT + "/div" + GT
            else:
                p1 = r['p'][0]
                w1 = int(p1['width'] * sx)
                h += LT + f"div class='p-un' style='left:0;top:{pt}px;width:{w1}px;height:{bh}px;'" + GT + f"{p1['name']}" + LT + "br" + GT + f"{p1['wt']}k" + LT + "/div" + GT
        else:
            p1 = r['p'][0]
            w1 = int(p1['width'] * sx)
            pl = int((cw - w1) / 2)
            h += LT + f"div class='p-un p-sng' style='left:{pl}px;top:{pt}px;width:{w1}px;height:{bh}px;'" + GT + f"{p1['name']}" + LT + "br" + GT + f"{p1['wt']}k" + LT + "/div" + GT
        cy += rl
        
    h += LT + "/div" + GT + "<div>USI SPATE</div>"
    st.markdown(h, unsafe_allow_html=True)
