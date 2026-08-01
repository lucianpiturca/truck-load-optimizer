# optimizer.py

from typing import List

from cargo import CargoItem, Pallet, expand_manifest

from packing import (
    pack_pallets,
    LayoutResult
)

from axles import (
    calculate_axle_weights,
    axle_score,
    is_legal
)


# ==========================================================
# OPTIMIZATION RESULT
# ==========================================================


class OptimizationResult:

    def __init__(

        self,

        best,

        second_best,

        rejected

    ):

        self.best = best

        self.second_best = second_best

        self.rejected = rejected



# ==========================================================
# INTERNAL SCORING
# ==========================================================


def layout_score(

    layout,

    axle_report

):

    """
    Overall solution score.

    Higher = better.

    Priorities:

    1. Legal axles
    2. More pallets loaded
    3. Height priority
    4. Less wasted space
    """



    score = 0



    # --------------------------
    # Axle legality
    # --------------------------

    score += axle_score(

        axle_report

    )



    # --------------------------
    # Number of pallets
    # --------------------------

    score += (

        len(layout.pallets)

        *

        20

    )



    # --------------------------
    # Height priority
    # --------------------------

    total_height = sum(

        pallet.height

        for pallet in layout.pallets

    )


    score += (

        total_height

        *

        0.01

    )



    # --------------------------
    # Space efficiency
    # --------------------------

    score += (

        layout.utilisation

        *

        50

    )



    return round(

        score,

        2

    )



# ==========================================================
# TRY ONE SOLUTION
# ==========================================================


def create_solution(

    truck,

    pallets

):


    layout = pack_pallets(

        truck,

        pallets

    )



    report = calculate_axle_weights(

        truck,

        layout.pallets

    )



    layout.score = layout_score(

        layout,

        report

    )


    return layout, report



# ==========================================================
# MAIN OPTIMIZER
# ==========================================================


def optimize_load(

    truck,

    cargo_items: List[CargoItem]

):


    """
    Generate possible loading solutions.

    Returns:

    best solution

    second best solution

    rejected cargo

    """



    all_pallets = expand_manifest(

        cargo_items

    )



    solutions = []



    rejected = []



    # ------------------------------------------------------
    # Different sorting strategies
    #
    # Later we can increase this to hundreds
    # of combinations.
    # ------------------------------------------------------


    strategies = [


        # Height first

        sorted(

            all_pallets,

            key=lambda p:

                p.height,

            reverse=True

        ),



        # Weight first

        sorted(

            all_pallets,

            key=lambda p:

                p.weight,

            reverse=True

        ),



        # Area first

        sorted(

            all_pallets,

            key=lambda p:

                p.width * p.length,

            reverse=True

        )

    ]



    for strategy in strategies:



        # Make copies

        pallets = [

            Pallet(

                id=p.id,

                description=p.description,

                width=p.width,

                length=p.length,

                height=p.height,

                weight=p.weight,

                allow_rotation=p.allow_rotation

            )

            for p in strategy

        ]



        layout, report = create_solution(

            truck,

            pallets

        )



        if len(layout.pallets) > 0:


            solutions.append(

                (

                    layout,

                    report

                )

            )



    # ------------------------------------------------------
    # Sort solutions
    # ------------------------------------------------------


    solutions.sort(

        key=lambda x:

            x[0].score,

        reverse=True

    )



    # ------------------------------------------------------
    # Best and second best
    # ------------------------------------------------------


    best = None

    second = None



    if len(solutions) >= 1:

        best = solutions[0]



    if len(solutions) >= 2:

        second = solutions[1]



    # ------------------------------------------------------
    # Find rejected pallets
    # ------------------------------------------------------


    if best:


        loaded_ids = [

            p.id

            for p in best[0].pallets

        ]



        for pallet in all_pallets:


            if pallet.id not in loaded_ids:


                pallet.reject_reason = (

                    "Could not fit legally"

                )


                rejected.append(

                    pallet

                )



    else:


        rejected = all_pallets



    return OptimizationResult(

        best,

        second,

        rejected

    )