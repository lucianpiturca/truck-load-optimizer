# drawing.py

import matplotlib.pyplot as plt
import matplotlib.patches as patches

from truck import Truck
from packing import LayoutResult


COLOUR_MAP = {}

COLORS = [
    "#4CAF50",
    "#2196F3",
    "#FF9800",
    "#9C27B0",
    "#F44336",
    "#00BCD4",
    "#795548",
]


def get_colour(description):

    if description not in COLOUR_MAP:

        COLOUR_MAP[description] = COLORS[
            len(COLOUR_MAP) % len(COLORS)
        ]

    return COLOUR_MAP[description]



def draw_trailer(truck: Truck, layout: LayoutResult):


    fig, ax = plt.subplots(

        figsize=(5,10),

        dpi=150

    )


    # ==================================================
    # Trailer outline
    # ==================================================

    trailer = patches.Rectangle(

        (0,0),

        truck.trailer_width,

        truck.trailer_length,

        linewidth=2,

        edgecolor="black",

        facecolor="#f8f8f8"

    )

    ax.add_patch(trailer)



    # ==================================================
    # Pallets
    # ==================================================

    for pallet in layout.pallets:


        visual_y = (

            truck.trailer_length

            -

            pallet.y

            -

            pallet.length

        )


        rect = patches.Rectangle(

            (
                pallet.x,
                visual_y
            ),

            pallet.width,

            pallet.length,

            linewidth=1,

            edgecolor="black",

            facecolor=get_colour(
                pallet.description
            ),

            alpha=0.85

        )

        ax.add_patch(rect)



        ax.text(

            pallet.x + pallet.width / 2,

            visual_y + pallet.length / 2,

            (
                f"#{pallet.id}\n"
                f"{int(pallet.width*100)}x"
                f"{int(pallet.length*100)}"
            ),

            ha="center",

            va="center",

            fontsize=5,

            color="white",

            weight="bold"

        )



    # ==================================================
    # Metre guide lines
    # ==================================================

    for metre in range(

        1,

        int(truck.trailer_length)+1

    ):


        visual_y = truck.trailer_length - metre


        ax.plot(

            [
                0,
                truck.trailer_width
            ],

            [
                visual_y,
                visual_y
            ],

            linestyle=":",

            linewidth=0.7,

            color="#cccccc"

        )


        ax.text(

            -0.12,

            visual_y,

            f"{metre}m",

            ha="right",

            va="center",

            fontsize=6,

            color="#888888"

        )



    # ==================================================
    # Front / Back labels
    # ==================================================

    ax.text(

        truck.trailer_width / 2,

        truck.trailer_length + 0.12,

        "🚛 FRONT (Kingpin)",

        ha="center",

        va="bottom",

        fontsize=8,

        weight="bold"

    )


    ax.text(

        truck.trailer_width / 2,

        -0.12,

        "BACK (Doors)",

        ha="center",

        va="top",

        fontsize=8,

        weight="bold"

    )



    # ==================================================
    # Compact layout
    # ==================================================

    ax.set_xlim(

        -0.45,

        truck.trailer_width + 0.05

    )


    ax.set_ylim(

        -0.35,

        truck.trailer_length + 0.35

    )


    ax.set_aspect(

        "equal"

    )


    ax.axis(

        "off"

    )


    fig.subplots_adjust(

        left=0.15,

        right=0.98,

        top=0.97,

        bottom=0.03

    )


    return fig