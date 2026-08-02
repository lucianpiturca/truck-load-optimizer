# drawing.py
# Truck Load Optimizer 2.0
#
# Trailer visualisation


import plotly.graph_objects as go

from truck import Truck
from packing import Layout



# ==========================================================
# COLOURS
# ==========================================================


TRAILER_COLOR = "#f5f5f5"

PALLET_COLOR = "#b8d8ff"

PALLET_ROTATED = "#ffd59a"

LINE_COLOR = "#999999"



# ==========================================================
# DRAW TRAILER
# ==========================================================


def create_loading_figure(
    truck: Truck,
    layout: Layout
):


    fig = go.Figure()



    # ------------------------------------------------------
    # Trailer outline
    # ------------------------------------------------------

    fig.add_shape(

        type="rect",

        x0=0,

        x1=truck.internal_width,

        y0=0,

        y1=truck.internal_length,

        fillcolor=TRAILER_COLOR,

        line=dict(
            color="#444",
            width=2
        )

    )



    # ------------------------------------------------------
    # Meter grid outside trailer
    # ------------------------------------------------------

    for m in range(

        1,

        int(truck.internal_length)+1

    ):

        fig.add_annotation(

            x=-0.15,

            y=m,

            text=f"{m}m",

            showarrow=False,

            font=dict(
                size=10,
                color="#555"
            )

        )



        fig.add_shape(

            type="line",

            x0=0,

            x1=truck.internal_width,

            y0=m,

            y1=m,

            line=dict(

                color="#cccccc",

                width=1,

                dash="dot"

            )

        )



    # ------------------------------------------------------
    # Front / rear labels
    # ------------------------------------------------------

    fig.add_annotation(

        x=truck.internal_width/2,

        y=-0.45,

        text="FRONT / CAB",

        showarrow=False,

        font=dict(
            size=12,
            color="black"
        )

    )


    fig.add_annotation(

        x=truck.internal_width/2,

        y=truck.internal_length+0.45,

        text="BACK DOORS",

        showarrow=False,

        font=dict(
            size=12,
            color="black"
        )

    )



    # ------------------------------------------------------
    # Pallets
    # ------------------------------------------------------

    for pallet in layout.pallets:


        length = pallet.draw_length

        width = pallet.draw_width



        colour = (

            PALLET_ROTATED

            if pallet.rotated

            else PALLET_COLOR

        )


        fig.add_shape(

            type="rect",

            x0=pallet.y,

            x1=pallet.y + length,

            y0=pallet.x,

            y1=pallet.x + width,

            fillcolor=colour,

            line=dict(

                color="#555",

                width=1

            )

        )


        label = (

            f"{pallet.description}<br>"

            f"{pallet.length:.2f}×"

            f"{pallet.width:.2f} m<br>"

            f"{pallet.weight:.0f} kg"

        )


        if pallet.rotated:

            label += "<br>↻ rotated"



        fig.add_annotation(

            x=pallet.y + length/2,

            y=pallet.x + width/2,

            text=label,

            showarrow=False,

            font=dict(

                size=8,

                color="black"

            )

        )



    # ------------------------------------------------------
    # Layout settings
    # ------------------------------------------------------

    fig.update_xaxes(

        visible=False,

        range=[

            -0.8,

            truck.internal_length + 0.8

        ]

    )


    fig.update_yaxes(

        visible=False,

        range=[

            truck.internal_width + 0.5,

            -0.5

        ],

        scaleanchor="x",

        scaleratio=1

    )



    fig.update_layout(

        width=650,

        height=850,

        margin=dict(

            l=20,

            r=20,

            t=40,

            b=40

        ),

        showlegend=False

    )



    return fig