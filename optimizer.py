# optimizer.py
# Truck Load Optimizer 2.0
#
# Maximum legal loading search


from dataclasses import dataclass, field
from typing import List


from cargo import Pallet

from truck import Truck

from packing import (
    pack_pallets,
    Layout,
    clone_layout
)

from axles import (
    calculate_axle_weights,
    check_axles_legal
)



# ==========================================================
# RESULT OBJECT
# ==========================================================


@dataclass
class OptimizationResult:

    best: Layout | None = None

    second_best: Layout | None = None

    axle_report = None

    rejected: List[Pallet] = field(
        default_factory=list
    )

    message: str = ""



# ==========================================================
# SORTING
# ==========================================================


def loading_priority(
    pallets: List[Pallet]
):

    """
    Heavy pallets first.

    Later:
    - stability score
    - CG optimisation
    - pallet grouping
    """


    return sorted(

        pallets,

        key=lambda p:

        (

            -p.weight,

            -(p.length * p.width)

        )

    )



# ==========================================================
# LEGAL TEST
# ==========================================================


def legal_layout(
    truck: Truck,
    layout: Layout
):


    report = calculate_axle_weights(

        truck,

        layout.pallets

    )


    legal = check_axles_legal(

        truck,

        report

    )


    return legal, report



# ==========================================================
# GREEDY LEGAL LOADING
# ==========================================================


def build_legal_load(
    truck: Truck,
    pallets: List[Pallet]
):


    loaded = []


    rejected = []



    ordered = loading_priority(

        pallets

    )



    for pallet in ordered:


        test = loaded + [pallet]


        test_layout = pack_pallets(

            truck,

            test

        )


        legal, report = legal_layout(

            truck,

            test_layout

        )


        if legal:


            loaded = [

                p

                for p in test_layout.pallets

            ]


        else:


            pallet.reason_not_loaded = (
                "Axle or gross weight exceeded"
            )


            rejected.append(

                pallet

            )



    final_layout = pack_pallets(

        truck,

        loaded

    )


    return (

        final_layout,

        rejected

    )



# ==========================================================
# PUBLIC API
# ==========================================================


def optimize_load(

    truck: Truck,

    pallets: List[Pallet]

):


    result = OptimizationResult()



    best, rejected = build_legal_load(

        truck,

        pallets

    )



    if best.pallet_count == 0:


        result.message = (

            "No legal loading solution found."

        )


        result.rejected = rejected


        return result



    result.best = best


    result.rejected.extend(

        rejected

    )


    result.axle_report = calculate_axle_weights(

        truck,

        best.pallets

    )


    result.message = (

        f"Loaded {best.pallet_count} pallets."

    )


    return result