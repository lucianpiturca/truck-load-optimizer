# drawing.py

import matplotlib.pyplot as plt
import matplotlib.patches as patches

from packing import LayoutResult
from truck import Truck



# ==========================================================
# COLOURS
# ==========================================================

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

        COLOUR_MAP[description] = (

            DEFAULT_COLOURS[

                len(COLOUR_MAP)

                %

                len(DEFAULT_COLOURS)

            ]

        )


    return COLOUR_MAP[description]



# ==========================================================
# DRAW TRAILER
# ==========================================================


def draw_trailer(

    truck: Truck,

    layout: LayoutResult

):


    fig, ax = plt.subplots(

        figsize=(8, 14)

    )



    # Trailer outline

    trailer = patches.Rectangle(

        (

            0,

            0

        ),

        truck.trailer_width,

        truck.trailer_length,

        linewidth=2,

        edgecolor="black",

        facecolor="#f7f7f7"

    )


    ax.add_patch(

        trailer

    )



    # ------------------------------------------------------
    # metre grid
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

            linewidth=0.7,

            color="#cccccc"

        )


        ax.text(

            truck.trailer_width/2,

            metre-0.05,

            f"{metre} m",

            ha="center",

            va="top",

            fontsize=7,

            color="#999999"

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

            alpha=0.75

        )


        ax.add_patch(

            rect

        )


        ax.text(

            pallet.x + pallet.width/2,

            pallet.y + pallet.length/2,

            str(pallet.id),

            ha="center",

            va="center",

            fontsize=8,

            color="white",

            weight="bold"

        )



    # ------------------------------------------------------
    # dimensions
    # ------------------------------------------------------


    ax.text(

        truck.trailer_width/2,

        truck.trailer_length + 0.3,

        (

            f"Used: {layout.used_length:.2f} m   |   "

            f"Free: {layout.free_length:.2f} m"

        ),

        ha="center",

        fontsize=10,

        weight="bold"

    )



    # ------------------------------------------------------
    # formatting
    # ------------------------------------------------------

    ax.set_xlim(

        -0.2,

        truck.trailer_width + 0.2

    )


    ax.set_ylim(

        -0.5,

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



# ==========================================================
# COMPARISON VIEW
# ==========================================================


def draw_two_solutions(

    truck,

    first,

    second

):


    fig, axes = plt.subplots(

        1,

        2,

        figsize=(12,12)

    )


    for ax, layout, title in [

        (

            axes[0],

            first,

            "Solution 1"

        ),

        (

            axes[1],

            second,

            "Solution 2"

        )

    ]:


        trailer = patches.Rectangle(

            (

                0,

                0

            ),

            truck.trailer_width,

            truck.trailer_length,

            linewidth=2,

            edgecolor="black",

            facecolor="#f7f7f7"

        )


        ax.add_patch(

            trailer

        )


        for pallet in layout.pallets:


            rect = patches.Rectangle(

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


            ax.add_patch(rect)



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

        ax.axis(

            "off"

        )


    plt.tight_layout()


    return fig