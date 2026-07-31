import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def draw_trailer(truck, cargo=None):

    if cargo is None:
        cargo = []

    fig, ax = plt.subplots(figsize=(16, 4))

    trailer_length = truck.trailer_length
    trailer_width = truck.trailer_width

    # Trailer floor
    ax.add_patch(
        Rectangle(
            (0, 0),
            trailer_length,
            trailer_width,
            facecolor="#f5f5f5",
            edgecolor="black",
            linewidth=2
        )
    )

    # Front wall
    ax.plot([0, 0], [0, trailer_width], linewidth=5, color="black")

    # Rear doors
    ax.plot(
        [trailer_length, trailer_length],
        [0, trailer_width],
        linewidth=5,
        color="gray"
    )

    # Draw pallets
    colors = [
        "#4CAF50",
        "#2196F3",
        "#FF9800",
        "#9C27B0",
        "#F44336",
        "#009688",
        "#795548",
    ]

    for i, pallet in enumerate(cargo):

        color = colors[i % len(colors)]

        ax.add_patch(
            Rectangle(
                (pallet["x"], pallet["y"]),
                pallet["length"],
                pallet["width"],
                facecolor=color,
                edgecolor="black"
            )
        )

        ax.text(
            pallet["x"] + pallet["length"]/2,
            pallet["y"] + pallet["width"]/2,
            pallet["label"],
            ha="center",
            va="center",
            fontsize=8,
            color="white",
            weight="bold"
        )

    ax.set_xlim(-0.5, trailer_length + 0.5)
    ax.set_ylim(-0.2, trailer_width + 0.2)

    ax.set_aspect("equal")

    ax.set_xticks(range(0, int(trailer_length)+1))
    ax.set_yticks([])

    ax.set_xlabel("Length (m)")

    plt.tight_layout()

    return fig