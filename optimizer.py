from packing import pack_cargo
from axles import calculate_axle_loads, check_axles



def calculate_score(pallets, axle_results, truck):

    score = 0


    # ---------------------------------
    # Axle legality
    # ---------------------------------

    for axle in axle_results:

        if not axle["legal"]:

            score -= 100000

        else:

            remaining = (

                axle["limit"]

                -

                axle["weight"]

            )

            score += remaining



    # ---------------------------------
    # Prefer taller pallets forward
    # ---------------------------------

    for pallet in pallets:


        distance_from_front = (

            truck.trailer_length

            -

            pallet["x"]

        )


        score += (

            pallet["height"]

            *

            distance_from_front

            *

            0.05

        )



    # ---------------------------------
    # Prefer compact loading
    # ---------------------------------

    if pallets:

        used_length = max(

            p["x"] + p["length"]

            for p in pallets

            if p["length"] > 0

        )


        score -= used_length * 10



    return score





def optimize_load(truck, manifest):


    candidates = []



    # Original order

    candidates.append(

        manifest.copy()

    )



    # Tallest first

    if "Height (cm)" in manifest.columns:

        candidates.append(

            manifest.sort_values(

                by="Height (cm)",

                ascending=False

            ).copy()

        )



    # Heaviest first

    if "Weight (kg)" in manifest.columns:

        candidates.append(

            manifest.sort_values(

                by="Weight (kg)",

                ascending=False

            ).copy()

        )



    best_layout = None

    best_score = -999999999



    for candidate in candidates:


        pallets = pack_cargo(

            truck,

            candidate

        )


        axle_loads = calculate_axle_loads(

            truck,

            pallets

        )


        axle_results = check_axles(

            truck,

            axle_loads

        )


        score = calculate_score(

            pallets,

            axle_results,

            truck

        )



        if score > best_score:


            best_score = score

            best_layout = pallets



    return best_layout