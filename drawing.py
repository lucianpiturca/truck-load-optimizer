# ==========================================================
# drawing.py
# Truck Load Optimizer
# Trailer visualisation
# ==========================================================


import plotly.graph_objects as go

from truck import Truck
from packing import Layout



PALLET_COLOUR = "#9ecae1"
PALLET_BORDER = "#1f4e79"
GRID_COLOUR = "#d6d6d6"



def pallet_font_size(layout):

    count = layout.pallet_count

    if count <= 10:
        return 14

    if count <= 20:
        return 12

    if count <= 35:
        return 11

    return 9



def create_loading_figure(

    truck: Truck,

    layout: Layout

):


    fig = go.Figure()



    # Trailer

    fig.add_shape(

        type="rect",

        x0=0,

        x1=truck.trailer_width,

        y0=0,

        y1=truck.trailer_length,

        line=dict(

            color="black",

            width=2

        ),

        fillcolor="#fafafa"

    )



    # metre grid

    for metre in range(

        1,

        int(truck.trailer_length)+1

    ):

        fig.add_shape(

            type="line",

            x0=0,

            x1=truck.trailer_width,

            y0=metre,

            y1=metre,

            line=dict(

                color=GRID_COLOUR,

                width=1,

                dash="dot"

            )

        )



    # pallets

    font_size = pallet_font_size(layout)


    for pallet in layout.pallets:


        x0 = pallet.x

        x1 = pallet.x + pallet.draw_width


        y0 = pallet.y

        y1 = pallet.y + pallet.draw_length



        fig.add_shape(

            type="rect",

            x0=x0,

            x1=x1,

            y0=y0,

            y1=y1,

            fillcolor=PALLET_COLOUR,

            line=dict(

                color=PALLET_BORDER,

                width=1

            )

        )


        fig.add_annotation(

            x=(x0+x1)/2,

            y=(y0+y1)/2,

            text=(

                f"{pallet.description}"

                f"<br>"

                f"{int(pallet.length*100)}x"

                f"{int(pallet.width*100)}"

                f"<br>"

                f"{int(pallet.weight)}kg"

            ),

            showarrow=False,

            font=dict(

                size=font_size,

                color="black"

            ),

            align="center"

        )



    # labels

    fig.add_annotation(

        x=truck.trailer_width/2,

        y=-0.18,

        text="FRONT",

        showarrow=False,

        font=dict(

            size=14

        )

    )


    fig.add_annotation(

        x=truck.trailer_width/2,

        y=truck.trailer_length+0.18,

        text="BACK DOORS",

        showarrow=False,

        font=dict(

            size=11

        )

    )



    # metre labels

    for metre in range(

        1,

        int(truck.trailer_length)+1

    ):

        fig.add_annotation(

            x=truck.trailer_width+0.12,

            y=metre,

            text=f"{metre}m",

            showarrow=False,

            font=dict(

                size=10,

                color="#666666"

            )

        )



    # Keep correct proportions but enlarge display

    fig.update_xaxes(

        visible=False,

        range=[

            -0.25,

            truck.trailer_width+0.45

        ]

    )


    fig.update_yaxes(

        visible=False,

        range=[

            truck.trailer_length+0.30,

            -0.30

        ],

        scaleanchor="x",

        scaleratio=1

    )



    fig.update_layout(

        height=1100,

        width=650,

        margin=dict(

            l=5,

            r=5,

            t=5,

            b=5

        ),

        showlegend=False,

        plot_bgcolor="white"

    )


    return fig