from packing import pack_cargo
from axles import (
    calculate_axle_loads,
    check_axles,
    calculate_gross_weight
)



def pallet_weight(pallet):

    return pallet.get(
        "weight",
        0
    )



def legal_axles(truck, pallets):

    axle_loads = calculate_axle_loads(
        truck,
        pallets
    )


    results = check_axles(

        truck,

        axle_loads

    )


    return all(

        axle["legal"]

        for axle in results

    )



def optimize_load(truck, manifest):

    """
    Loads maximum legal cargo.

    Priority:

    1. Keep axle weights legal
    2. Keep total weight legal
    3. Use available space
    4. Prefer taller pallets first

    """


    loaded = []

    rejected = []



    if manifest.empty:

        return loaded



    # ---------------------------------
    # Expand pallet quantities
    # ---------------------------------

    pallet_list = []



    for _, row in manifest.iterrows():


        try:

            quantity = int(
                row["Pallet Quantity"]
            )

        except:

            continue



        for i in range(quantity):


            pallet_list.append(

                {

                    "Goods Description":
                        row["Goods Description"],


                    "Width (cm)":
                        row["Width (cm)"],


                    "Length (cm)":
                        row["Length (cm)"],


                    "Height (cm)":
                        row["Height (cm)"],


                    "Weight (kg)":
                        row["Weight (kg)"],


                    "Allow Rotation":
                        row["Allow Rotation"],


                }

            )



    # ---------------------------------
    # Priority:
    # height first, weight second
    # ---------------------------------

    pallet_list.sort(

        key=lambda x:

        (

            x["Height (cm)"],

            -x["Weight (kg)"]

        ),

        reverse=True

    )



    current_manifest = []



    for pallet in pallet_list:


        test_manifest = current_manifest + [pallet]



        df = manifest_from_list(

            test_manifest

        )



        layout = pack_cargo(

            truck,

            df

        )



        # remove pallets that do not fit physically

        layout = [

            p for p in layout

            if p["length"] > 0

        ]



        # Check space

        if len(layout) < len(test_manifest):


            rejected.append(

                {

                    "pallet": pallet,

                    "reason":

                    "No trailer space available"

                }

            )


            continue



        # Check weight

        gross = calculate_gross_weight(

            calculate_axle_loads(

                truck,

                layout

            )

        )



        if gross > truck.legal_gross:


            rejected.append(

                {

                    "pallet": pallet,

                    "reason":

                    "Maximum legal gross weight exceeded"

                }

            )


            continue



        # Check axles

        if not legal_axles(

            truck,

            layout

        ):


            rejected.append(

                {

                    "pallet": pallet,

                    "reason":

                    "Axle weight limit exceeded"

                }

            )


            continue



        # Accept pallet

        current_manifest.append(

            pallet

        )


    # ---------------------------------
    # Final packing
    # ---------------------------------

    final_df = manifest_from_list(

        current_manifest

    )


    loaded = pack_cargo(

        truck,

        final_df

    )


    loaded = [

        p for p in loaded

        if p["length"] > 0

    ]



    return loaded, rejected





def manifest_from_list(items):

    """
    Converts internal pallet list
    back into optimizer dataframe.
    """

    import pandas as pd



    return pd.DataFrame(

        [

            {

                "Goods Description":
                    p["Goods Description"],


                "Pallet Quantity":
                    1,


                "Width (cm)":
                    p["Width (cm)"],


                "Length (cm)":
                    p["Length (cm)"],


                "Height (cm)":
                    p["Height (cm)"],


                "Weight (kg)":
                    p["Weight (kg)"],


                "Allow Rotation":
                    p["Allow Rotation"]

            }

            for p in items

        ]

    )