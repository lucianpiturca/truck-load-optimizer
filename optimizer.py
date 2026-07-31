from packing import pack_cargo
from axles import calculate_axle_loads, check_axles


def calculate_score(pallets, axle_results, truck):

    """
    Higher score = better loading plan.

    Priorities:
    1. Legal axle loads
    2. Taller pallets forward
    3. Better trailer usage
    """

    score = 0


    # ---------------------------------
    # Penalize overweight axles heavily
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

        front_bonus = (

            truck.trailer_length

            -

            pallet["x"]

        )


        score += (

            pallet["height"]

            *

            front_bonus

            *

            0.1

        )


    # ---------------------------------
    # Prefer shorter used length
    # ---------------------------------

    if pallets:

        used = max(

            p["x"] + p["length"]

            for p in pallets

        )

        score -= used * 10


    return score





def optimize_load(truck, manifest):

    """
    First optimization version.

    Tests different cargo orders.

    Priority:
    1. Height
    2. Weight
    3. Space
    """


    candidates = []


    # ---------------------------------
    # Normal order
    # ---------------------------------

    candidates.append(manifest)



    # ---------------------------------
    # Tallest first
    # ---------------------------------

    candidates.append(

        manifest.sort_values(

            by="Height",

            ascending=False

        )

    )



    # ---------------------------------
    # Heaviest first
    # ---------------------------------

    candidates.append(

        manifest.sort_values(

            by="Weight",

            ascending=False

        )

    )



    best = None

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

            best = pallets



    return best