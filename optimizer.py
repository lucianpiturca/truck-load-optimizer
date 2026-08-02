# ==========================================================
# optimizer.py
# Truck Load Optimizer
#
# Main optimisation engine
# ==========================================================


from dataclasses import dataclass, field
from typing import List


from truck import Truck

from cargo import (
    CargoItem,
    Pallet,
    expand_cargo
)

from packing import (
    generate_candidates,
    Layout
)

from axles import (
    calculate_axle_weights,
    check_axle_legality,
    AxleReport
)



# ==========================================================
# RESULT OBJECT
# ==========================================================


@dataclass
class OptimizationResult:


    best: List[Layout] = field(

        default_factory=list

    )


    axle_report: AxleReport | None = None



    loaded_pallets: List[Pallet] = field(

        default_factory=list

    )


    rejected_pallets: List[Pallet] = field(

        default_factory=list

    )


    success: bool = False



    message: str = ""



# ==========================================================
# LAYOUT LEGALITY
# ==========================================================


def evaluate_layout(

    truck: Truck,

    layout: Layout

):


    report = calculate_axle_weights(

        truck,

        layout.pallets

    )


    report = check_axle_legality(

        truck,

        report

    )


    return (

        report.legal,

        report

    )



# ==========================================================
# SORTING
# ==========================================================


def layout_priority(

    layout: Layout,

    axle_report: AxleReport

):


    """
    Higher is better.

    Priority:

    1. number of pallets
    2. stability score
    3. floor usage
    4. lower centre of gravity
    """


    return (

        layout.pallet_count * 100000

        +

        layout.score * 100

        -

        axle_report.centre_of_gravity

    )



# ==========================================================
# MAIN OPTIMIZER
# ==========================================================


def optimize_load(

    truck: Truck,

    cargo_items: List[CargoItem]

):


    result = OptimizationResult()



    # ------------------------------------------------------
    # Create pallets
    # ------------------------------------------------------


    pallets = expand_cargo(

        cargo_items

    )



    if not pallets:


        result.message = "No cargo"


        return result



    # ------------------------------------------------------
    # Search from maximum quantity downward
    #
    # This allows:
    #
    # 34 requested
    # 33 legal
    #
    # instead of returning no solution.
    # ------------------------------------------------------


    pallets_sorted = sorted(

        pallets,

        key=lambda p:

        p.weight,

        reverse=True

    )



    for amount in range(

        len(pallets_sorted),

        0,

        -1

    ):


        trial = pallets_sorted[:amount]



        candidates = generate_candidates(

            truck,

            trial

        )



        legal_candidates = []



        for candidate in candidates:


            legal, axle = evaluate_layout(

                truck,

                candidate.layout

            )


            if legal:


                legal_candidates.append(

                    (

                        candidate.layout,

                        axle

                    )

                )



        if legal_candidates:


            best_layout, best_axle = sorted(

                legal_candidates,

                key=lambda x:

                layout_priority(

                    x[0],

                    x[1]

                ),

                reverse=True

            )[0]



            loaded_ids = set(

                id(p)

                for p in best_layout.pallets

            )



            rejected = [

                p

                for p in pallets

                if id(p)

                not in loaded_ids

            ]



            result.best = [

                best_layout

            ]


            result.axle_report = best_axle


            result.loaded_pallets = (

                best_layout.pallets

            )


            result.rejected_pallets = rejected


            result.success = True


            result.message = (

                "Legal loading solution found"

            )


            return result



    # ------------------------------------------------------
    # No legal solution
    # ------------------------------------------------------


    for pallet in pallets:


        pallet.reason_not_loaded = (

            "Axle or gross weight exceeded"

        )



    result.rejected_pallets = pallets


    result.message = (

        "No legal loading solution found"

    )


    return result