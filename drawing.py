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


    # smaller visualization

    fig, ax = plt.subplots(

        figsize=(3.2, 5)

    )


    # ==================================================
    # Trailer outline
    # ==================================================

    trailer = patches.Rectangle(

        (0, 0),

        truck.trailer_width,

        truck.trailer_length,

        linewidth=2,

        edgecolor="black",

        facecolor="#fafafa"

    )

    ax.add_patch(trailer)



    # ==================================================
    # FRONT / BACK labels
    # ==================================================

    ax.text(

        truck.trailer_width / 2,

        truck.trailer_length + 0.35,

        "🚛 FRONT\n(kingpin)",

        ha="center",

        va="bottom",

        fontsize=8,

        weight="bold"

    )


    ax.text(

        truck.trailer_width / 2,

        -0.35,

        "BACK\n(doors)",

        ha="center",

        va="top",

        fontsize=8,

        weight="bold"

    )



    # ==================================================
    # metre lines + outside labels
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

            linewidth=0.7,

            color="#d0d0d0"

        )


        ax.text(

            -0.12,

            metre,

            f"{metre}m",

            ha="right",

            va="center",

            fontsize=6,

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

            linewidth=1,

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

            fontsize=3,

            color="white",

            weight="bold"

        )



    # ==================================================
    # Layout
    # ==================================================

    ax.set_xlim(

        -0.55,

        truck.trailer_width + 0.1

    )


    ax.set_ylim(

        -0.7,

        truck.trailer_length + 0.7

    )


    ax.set_aspect(

        "equal"

    )


    ax.axis(

        "off"

    )


    plt.tight_layout()


    return fig



def draw_two_solutions(

    truck,

    first,

    second

):


    fig, axes = plt.subplots(

        1,

        2,

        figsize=(7,5)

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

            facecolor="#fafafa"

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

                    facecolor=get_colour(

                        pallet.description

                    ),

                    edgecolor="black"

                )

            )


        ax.set_title(title)

        ax.set_xlim(

            -0.2,

            truck.trailer_width + 0.2

        )

        ax.set_ylim(

            -0.2,

            truck.trailer_length + 0.2

        )

        ax.set_aspect(

            "equal"

        )

        ax.axis("off")


    plt.tight_layout()


    return fig