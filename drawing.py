import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def draw_trailer(truck, cargo=None):

    if cargo is None:
        cargo = []


    trailer_length = truck.trailer_length
    trailer_width = truck.trailer_width


    fig, ax = plt.subplots(
        figsize=(16, 4)
    )


    # -----------------------------
    # Trailer floor
    # -----------------------------

    ax.add_patch(
        Rectangle(
            (0, 0),
            trailer_length,
            trailer_width,
            facecolor="#fafafa",
            edgecolor="black",
            linewidth=2
        )
    )


    # -----------------------------
    # Meter grid lines
    # -----------------------------

    for meter in range(
        1,
        int(trailer_length)
    ):

        ax.plot(
            [meter, meter],
            [0, trailer_width],

            linestyle=":",
            linewidth=0.8,
            color="lightgray",
            zorder=0
        )


        ax.text(
            meter,
            trailer_width + 0.05,

            str(meter),

            ha="center",
            va="bottom",

            fontsize=8,

            color="gray"
        )


    # Start marker

    ax.text(
        0,
        trailer_width + 0.05,

        "0",

        ha="center",
        fontsize=8,
        color="gray"
    )


    # -----------------------------
    # Trailer walls
    # -----------------------------

    # Front wall

    ax.plot(
        [0, 0],
        [0, trailer_width],

        color="black",
        linewidth=5
    )


    ax.text(
        0,
        trailer_width/2,

        "FRONT",

        rotation=90,

        fontsize=9,

        va="center",

        ha="right"
    )


    # Rear doors

    ax.plot(
        [trailer_length, trailer_length],
        [0, trailer_width],

        color="black",
        linewidth=5
    )


    ax.text(
        trailer_length,
        trailer_width/2,

        "REAR",

        rotation=90,

        fontsize=9,

        va="center",

        ha="left"
    )



    # -----------------------------
    # Draw pallets
    # -----------------------------

    colors = [

        "#1976D2",
        "#388E3C",
        "#F57C00",
        "#7B1FA2",
        "#C62828",
        "#00838F",
        "#5D4037"

    ]


    for index, pallet in enumerate(cargo):


        if pallet["length"] <= 0:
            continue


        color = colors[
            index % len(colors)
        ]


        ax.add_patch(
            Rectangle(

                (
                    pallet["x"],
                    pallet["y"]
                ),

                pallet["length"],

                pallet["width"],

                facecolor=color,

                edgecolor="black",

                linewidth=1

            )
        )


        # label

        label = (

            f'{pallet["label"]}\n'

            f'{int(pallet["length"]*100)}x'
            f'{int(pallet["width"]*100)} cm\n'

            f'{int(pallet["weight"])} kg\n'

            f'{int(pallet["height"])} cm'

        )


        ax.text(

            pallet["x"]
            +
            pallet["length"]/2,


            pallet["y"]
            +
            pallet["width"]/2,


            label,


            ha="center",

            va="center",

            fontsize=6,

            color="white",

            weight="bold"

        )



    # -----------------------------
    # Calculate used length
    # -----------------------------

    if cargo:

        valid = [

            p for p in cargo

            if p["length"] > 0

        ]


        if valid:

            used_length = max(

                p["x"] + p["length"]

                for p in valid

            )

        else:

            used_length = 0


    else:

        used_length = 0



    free_length = (
        trailer_length
        -
        used_length
    )


    # -----------------------------
    # Formatting
    # -----------------------------

    ax.set_xlim(
        -0.5,
        trailer_length + 0.5
    )


    ax.set_ylim(
        -0.2,
        trailer_width + 0.3
    )


    ax.set_aspect(
        "equal"
    )


    ax.axis(
        "off"
    )


    plt.tight_layout()


    return (
        fig,
        used_length,
        free_length
    )