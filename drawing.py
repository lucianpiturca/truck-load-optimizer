# drawing.py

import matplotlib.pyplot as plt
import matplotlib.patches as patches

from packing import LayoutResult
from truck import Truck


COLOUR_MAP = {}

DEFAULT_COLOURS = [
    "#4CAF50",
    "#2196F3",
    "#FF9800",
    "#9C27B0",
    "#F44336",
    "#00BCD4",
    "#795548"
]


def get_colour(description):

    if description not in COLOUR_MAP:

        COLOUR_MAP[description] = DEFAULT_COLOURS[
            len(COLOUR_MAP) % len(DEFAULT_COLOURS)
        ]

    return COLOUR_MAP[description]



# ==========================================================
# TRAILER DRAWING
# ==========================================================

def draw_trailer(

    truck: Truck,

    layout: LayoutResult

):


    # Smaller figure

    fig, ax = plt.subplots(

        figsize=(5, 9)

    )


    # ------------------------------------------------------
    # Trailer body
    # ------------------------------------------------------

    trailer = patches.Rectangle(

        (
            0,
            0
        ),

        truck.trailer_width,

        truck.trailer_length,

        linewidth=2,

        edgecolor="black",

        facecolor="#f8f8f8"

    )


    ax.add_patch(trailer)



    # ------------------------------------------------------
    # FRONT / BACK
    # ------------------------------------------------------

    ax.text(

        truck.trailer_width / 2,

        truck.trailer_length + 0.35,

        "🚛 FRONT (kingpin side)",

        ha="center",

        fontsize=10,

        weight="bold"

    )


    ax.text(

        truck.trailer_width / 2,

        -0.45,

        "BACK (trailer doors)",

        ha="center",

        fontsize=10,

        weight="bold"

    )



    # ------------------------------------------------------
    # metre dotted lines
    # ------------------------------------------------------

    for metre in range(

        1,

        int(truck.trailer_length)+1

    ):


        ax.plot(

            [
                0,
                truck.trailer_width
            ],

            [
                metre,
                metre
            ],

            linestyle=":",

            linewidth=0.8,

            color="#d0d0d0"

        )


        # outside label

        ax.text(

            -0.25,

            metre,

            f"{metre}m",

            va="center",

            ha="right",

            fontsize=8,

            color="#777777"

        )



    # ------------------------------------------------------
    # pallets
    # ------------------------------------------------------

    for pallet in layout.pallets:


        colour = get_colour(

            pallet.description

        )


        rect = patches.Rectangle(

            (
                pallet.x,

                pallet.y

            ),

            pallet.width,

            pallet.length,

            linewidth=1,

            edgecolor="black",

            facecolor=colour,

            alpha=0.8

        )


        ax.add_patch(rect)



        label = (

            f"{pallet.description}\n"

            f"{int(pallet.width*100)}×"

            f"{int(pallet.length*100)} cm\n"

            f"{pallet.id}"

        )


        ax.text(

            pallet.x + pallet.width/2,

            pallet.y + pallet.length/2,

            label,

            ha="center",

            va="center",

            fontsize=6,

            color="white",

            weight="bold"

        )



    # ------------------------------------------------------
    # formatting
    # ------------------------------------------------------

    ax.set_xlim(

        -0.8,

        truck.trailer_width + 0.2

    )


    ax.set_ylim(

        -0.8,

        truck.trailer_length + 0.8

    )


    ax.set_aspect(

        "equal"

    )


    ax.axis(

        "off"

    )


    plt.tight_layout()


    return fig