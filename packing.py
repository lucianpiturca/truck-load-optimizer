def try_position(
    pallets,
    pallet_length,
    pallet_width,
    trailer_length,
    trailer_width
):
    """
    Checks if a pallet can fit without overlapping.
    """

    step = 0.05   # 5 cm positioning accuracy


    x = 0.0

    while x + pallet_length <= trailer_length:


        y = 0.0

        while y + pallet_width <= trailer_width:


            collision = False


            for p in pallets:


                if p["length"] == 0:

                    continue


                overlap_x = not (

                    x + pallet_length <= p["x"]

                    or

                    x >= p["x"] + p["length"]

                )


                overlap_y = not (

                    y + pallet_width <= p["y"]

                    or

                    y >= p["y"] + p["width"]

                )


                if overlap_x and overlap_y:

                    collision = True

                    break



            if not collision:


                return {

                    "x": x,

                    "y": y

                }



            y += step


        x += step



    return None





def calculate_used_length(pallets):

    """
    Returns occupied trailer length in metres.
    """


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





def pack_cargo(truck, manifest):

    """
    Improved pallet packing.

    Priority:
    1. Fit pallet
    2. Test rotation
    3. Choose shortest trailer usage

    Each pallet can rotate independently.
    """



    pallets = []

    pallet_id = 1



    trailer_length = truck.trailer_length

    trailer_width = truck.trailer_width



    if manifest.empty:

        return pallets



    for _, item in manifest.iterrows():


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


            allow_rotation = bool(

                item["Allow Rotation"]

            )


        except Exception:


            continue




        for number in range(quantity):


            options = []



            # Normal orientation

            options.append(

                {

                    "length": length,

                    "width": width,

                    "rotated": False

                }

            )



            # Rotated orientation

            if allow_rotation and length != width:


                options.append(

                    {

                        "length": width,

                        "width": length,

                        "rotated": True

                    }

                )



            best = None

            best_score = None



            for option in options:



                position = try_position(

                    pallets,

                    option["length"],

                    option["width"],

                    trailer_length,

                    trailer_width

                )



                if position is None:

                    continue



                test_length = max(

                    calculate_used_length(pallets),

                    position["x"] + option["length"]

                )



                score = test_length



                if best_score is None or score < best_score:


                    best_score = score


                    best = {

                        **option,

                        **position

                    }




            if best is not None:


                pallets.append(

                    {

                        "id": pallet_id,

                        "label":

                            f"{description}-{number+1}",


                        "x":

                            best["x"],


                        "y":

                            best["y"],


                        "length":

                            best["length"],


                        "width":

                            best["width"],


                        "weight":

                            weight,


                        "height":

                            height,


                        "rotated":

                            best["rotated"]

                    }

                )



            else:


                # pallet cannot fit

                pallets.append(

                    {

                        "id": pallet_id,

                        "label": "NOT FIT",

                        "x": 0,

                        "y": 0,

                        "length": 0,

                        "width": 0,

                        "weight": weight,

                        "height": height,

                        "rotated": False

                    }

                )



            pallet_id += 1



    return pallets