"""Professional top-down trailer load-plan visualization."""

import hashlib

import plotly.graph_objects as go

from packing import Layout
from truck import Truck


PALETTE = ["#4C78A8", "#59A14F", "#E39C37", "#AF7AA1", "#E15759", "#76B7B2"]
NAVY = "#102A43"
GRID = "#D9E2EC"


def pallet_font_size(layout):
    if layout.pallet_count <= 10:
        return 12
    if layout.pallet_count <= 20:
        return 10
    return 8


def pallet_colour(description):
    digest = hashlib.sha256(description.encode("utf-8")).digest()[0]
    return PALETTE[digest % len(PALETTE)]


def pallet_label(pallet):
    description = pallet.description
    if len(description) > 17:
        description = f"{description[:15]}…"
    return f"<b>{description}</b><br>{pallet.draw_length * 100:.0f} × {pallet.draw_width * 100:.0f} cm<br>{pallet.weight:,.0f} kg"


def create_loading_figure(truck: Truck, layout: Layout):
    """Return a top-down Plotly figure of the physical loading plan."""
    fig = go.Figure()
    fig.add_shape(type="rect", x0=0, x1=truck.trailer_width, y0=0, y1=truck.trailer_length,
                  line=dict(color=NAVY, width=2.5), fillcolor="#FFFFFF", layer="below")
    for metre in range(1, int(truck.trailer_length) + 1):
        fig.add_shape(type="line", x0=0, x1=truck.trailer_width, y0=metre, y1=metre,
                      line=dict(color=GRID, width=1, dash="dot"), layer="below")

    kingpin_y = truck.trailer_front_offset
    bogie_y = truck.trailer_front_offset + truck.bogie_position
    for y, label, colour in ((kingpin_y, "KINGPIN", "#7B8794"), (bogie_y, "TRIDEM CENTRE", "#D64545")):
        if 0 < y < truck.trailer_length:
            fig.add_shape(type="line", x0=0, x1=truck.trailer_width, y0=y, y1=y,
                          line=dict(color=colour, width=1.2, dash="dash"))
            fig.add_annotation(x=truck.trailer_width + 0.06, y=y, text=label, showarrow=False,
                               xanchor="left", font=dict(size=9, color=colour))

    hover_x, hover_y, hover_text = [], [], []
    for pallet in layout.pallets:
        x0, y0 = pallet.x, pallet.y
        x1, y1 = x0 + pallet.draw_width, y0 + pallet.draw_length
        fig.add_shape(type="rect", x0=x0, x1=x1, y0=y0, y1=y1,
                      line=dict(color="#FFFFFF", width=1.5), fillcolor=pallet_colour(pallet.description))
        fig.add_annotation(x=(x0 + x1) / 2, y=(y0 + y1) / 2, text=pallet_label(pallet), showarrow=False,
                           font=dict(size=pallet_font_size(layout), color="#FFFFFF"), align="center")
        hover_x.append((x0 + x1) / 2)
        hover_y.append((y0 + y1) / 2)
        orientation = "Rotated" if pallet.rotated else "Standard"
        hover_text.append(f"<b>{pallet.description}</b><br>Position: {pallet.y:.2f} m from front<br>"
                          f"Dimensions: {pallet.draw_length:.2f} × {pallet.draw_width:.2f} m<br>"
                          f"Weight: {pallet.weight:,.0f} kg<br>Orientation: {orientation}")

    fig.add_trace(go.Scatter(x=hover_x, y=hover_y, mode="markers",
                              marker=dict(size=18, color="rgba(0,0,0,0.01)"), hovertext=hover_text,
                              hovertemplate="%{hovertext}<extra></extra>", showlegend=False))
    fig.add_annotation(x=truck.trailer_width / 2, y=-0.30, text="FRONT BULKHEAD", showarrow=False,
                       font=dict(size=11, color=NAVY))
    fig.add_annotation(x=truck.trailer_width / 2, y=truck.trailer_length + 0.30, text="REAR DOORS", showarrow=False,
                       font=dict(size=11, color=NAVY))
    fig.update_xaxes(visible=False, range=[-0.08, truck.trailer_width + 0.50])
    fig.update_yaxes(visible=False, range=[truck.trailer_length + 0.45, -0.45], scaleanchor="x", scaleratio=1)
    fig.update_layout(height=max(760, int(truck.trailer_length * 58)), margin=dict(l=5, r=65, t=5, b=5),
                      showlegend=False, plot_bgcolor="#F5F7FA", paper_bgcolor="#F5F7FA",
                      hoverlabel=dict(bgcolor="#102A43", font_color="white", font_size=12))
    return fig
