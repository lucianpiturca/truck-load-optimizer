def pack_cargo(truck, manifest):
    """
    Basic pallet placement engine.

    Uses:
    - real trailer dimensions
    - pallet dimensions
    - optional rotation
    - pallet height
    - pallet weight

    Coordinates:
        x = trailer length direction (m)
        y = trailer width direction (m)
    """

    pallets = []


    if manifest.empty:
        return pallets


    trailer_length = truck.trailer_length
    trailer_width = truck.trailer_width


    current_x = 0.0
    current_y = 0.0

    row_length = 0.0

    pallet_id = 1



    for _, item in manifest.iterrows():


        # Skip incomplete rows

        try:

            quantity = int(
                item["Pallet Quantity"]
            )

            width = float(
                item["Width (cm)"]
            ) / 100


            length = float(
                item["Length (cm)"]
            ) / 100


            height = float(
                item["Height (cm)"]
            )


            weight = float(
                item["Weight (kg)"]
            )


            description = str(
                item["Goods Description"]
            )


            rotation_allowed = bool(
                item["Allow Rotation"]
            )


        except Exception:

            continue



        for number in range(quantity):


            placed = False


            # Possible orientations

            orientations = [

                (
                    length,
                    width
                )

            ]


            if rotation_allowed:

                orientations.append(

                    (
                        width,
                        length
                    )

                )



            for pallet_length, pallet_width in orientations:



                # Need next row?

                if (
                    current_y
                    +
                    pallet_width
                    >
                    trailer_width
                ):


                    current_x += row_length

                    current_y = 0

                    row_length = 0



                # Check trailer length

                if (
                    current_x
                    +
                    pallet_length
                    <=
                    trailer_length
                ):


                    pallets.append(

                        {

                            "id":
                                pallet_id,


                            "label":
                                f"{description}-{number+1}",


                            "x":
                                current_x,


                            "y":
                                current_y,


                            "length":
                                pallet_length,


                            "width":
                                pallet_width,


                            "weight":
                                weight,


                            "height":
                                height

                        }

                    )


                    current_y += pallet_width


                    row_length = max(

                        row_length,

                        pallet_length

                    )


                    pallet_id += 1


                    placed = True


                    break



            # If pallet cannot fit

            if not placed:


                pallets.append(

                    {

                        "id":
                            pallet_id,


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

                    }

                )


                pallet_id += 1



    return pallets





def calculate_used_length(pallets):

    """
    Calculates occupied trailer length.
    """


    valid_pallets = [

        p for p in pallets

        if p["length"] > 0

    ]


    if not valid_pallets:

        return 0



    return max(

        p["x"] + p["length"]

        for p in valid_pallets

    )