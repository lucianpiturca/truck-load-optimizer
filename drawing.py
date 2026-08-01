# drawing.py

import matplotlib.pyplot as plt
import matplotlib.patches as patches

from packing import LayoutResult
from truck import Truck


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



def draw_trailer(

    truck: Truck,

    layout: LayoutResult

):


    fig, ax = plt.subplots(

        figsize=(2.8, 4.5)

    )


    # ==================================================
    # Trailer
    # ==================================================

    trailer = patches.Rectangle(

        (0, 0),

        truck.trailer_width,

        truck.trailer_length,

        linewidth=1.8,

        edgecolor="black",

        facecolor="#f8f8f8"

    )


    ax.add_patch(trailer)



    # ==================================================
    # FRONT / BACK
    #
    # y=0 = FRONT
    # y=max = BACK
    # ==================================================

    ax.text(

        truck.trailer_width / 2,

        -0.25,

        "🚛 FRONT\nKingpin",

        ha="center",

        va="top",

        fontsize=7,

        weight="bold"

    )


    ax.text(

        truck.trailer_width / 2,

        truck.trailer_length + 0.25,

        "BACK\nDoors",

        ha="center",

        va="bottom",

        fontsize=7,

        weight="bold"

    )



    # ==================================================
    # Meter grid
    # ==================================================

    for metre in range(

        1,

        int(truck.trailer_length) + 1

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

            linewidth=0.6,

            color="#d2d2d2"

        )


        ax.text(

            -0.12,

            metre,

            f"{metre}m",

            ha="right",

            va="center",

            fontsize=5,

            color="#888888"

        )



    # ==================================================
    # Pallets
    # ==================================================

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

            linewidth=0.8,

            edgecolor="black",

            facecolor=colour,

            alpha=0.85

        )


        ax.add_patch(rect)



        label = (

            f"#{pallet.id}\n"

            f"{int(pallet.width*100)}x"

            f"{int(pallet.length*100)}"

        )


        ax.text(

            pallet.x + pallet.width / 2,

            pallet.y + pallet.length / 2,

            label,

            ha="center",

            va="center",

            fontsize=2.5,

            color="white",

            weight="bold"

        )



    # ==================================================
    # Size control
    # ==================================================

    ax.set_xlim(

        -0.45,

        truck.trailer_width + 0.05

    )


    ax.set_ylim(

        -0.55,

        truck.trailer_length + 0.55

    )


    ax.set_aspect(

        "equal"

    )


    ax.axis(

        "off"

    )


    fig.subplots_adjust(

        left=0.20,

        right=0.98,

        top=0.92,

        bottom=0.08

    )


    return fig



def draw_two_solutions(

    truck,

    first,

    second

):


    fig, axes = plt.subplots(

        1,

        2,

        figsize=(6,4.5)

    )


    for ax, layout, title in [

        (axes[0], first, "Solution 1"),

        (axes[1], second, "Solution 2")

    ]:


        trailer = patches.Rectangle(

            (0,0),

            truck.trailer_width,

            truck.trailer_length,

            edgecolor="black",

            facecolor="#f8f8f8"

        )


        ax.add_patch(trailer)


        for pallet in layout.pallets:


            ax.add_patch(

                patches.Rectangle(

                    (

                        pallet.x,

                        pallet.y

                    ),

                    pallet.width,

                    pallet.length,

                    edgecolor="black",

                    facecolor=get_colour(

                        pallet.description

                    )

                )

            )


        ax.set_title(title)

        ax.set_xlim(

            0,

            truck.trailer_width

        )

        ax.set_ylim(

            0,

            truck.trailer_length

        )

        ax.set_aspect(

            "equal"

        )

        ax.axis("off")


    return fig