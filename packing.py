import pandas as pd


def pack_cargo(truck, manifest):
    """
    Basic pallet placement engine.

    Places pallets inside the trailer using:
    - real trailer dimensions
    - real pallet dimensions
    - rotation when allowed
    - pallet height and weight information

    Coordinates:
        x = trailer length direction (meters)
        y = trailer width direction (meters)
    """

    pallets = []

    trailer_length = truck.trailer_length
    trailer_width = truck.trailer_width


    current_x = 0.0
    current_y = 0.0

    row_length = 0.0

    pallet_counter = 1


    # Ignore empty manifest
    if manifest.empty:
        return pallets


    for _, item in manifest.iterrows():

        try:
            quantity = int(item["Qty"])

        except:
            continue


        pallet_width = float(item["Width"]) / 100
        pallet_length = float(item["Length"]) / 100


        height = float(item["Height"])

        weight = float(item["Weight"])


        allow_rotation = bool(item["Rotate"])


        for number in range(quantity):


            placed = False


            orientations = [
                (
                    pallet_length,
                    pallet_width
                )
            ]


            # Try rotated pallet
            if allow_rotation:

                orientations.append(
                    (
                        pallet_width,
                        pallet_length
                    )
                )


            for length, width in orientations:


                # Need new row?
                if current_y + width > trailer_width:


                    current_x += row_length

                    current_y = 0

                    row_length = 0


                # Does it fit in trailer length?
                if current_x + length <= trailer_length:


                    pallet = {

                        "id":
                            pallet_counter,


                        "label":
                            f"{item['Description']}-{number+1}",


                        "x":
                            current_x,


                        "y":
                            current_y,


                        "length":
                            length,


                        "width":
                            width,


                        "weight":
                            weight,


                        "height":
                            height

                    }


                    pallets.append(pallet)


                    current_y += width


                    row_length = max(
                        row_length,
                        length
                    )


                    pallet_counter += 1


                    placed = True

                    break


            # If pallet does not fit
            if not placed:

                pallets.append({

                    "id":
                        pallet_counter,

                    "label":
                        "NOT FIT",

                    "x":
                        0,

                    "y":
                        0,

                    "length":
                        0,

                    "width":
                        0,

                    "weight":
                        weight,

                    "height":
                        height
                })


                pallet_counter += 1


    return pallets



def calculate_used_length(pallets):

    """
    Calculates occupied trailer length.
    """

    if not pallets:
        return 0


    valid = [
        p for p in pallets
        if p["length"] > 0
    ]


    if not valid:
        return 0


    return max(
        p["x"] + p["length"]
        for p in valid
    )