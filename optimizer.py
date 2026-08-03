# ==========================================================
# optimizer.py
# Truck Load Optimizer
# ==========================================================


from dataclasses import dataclass, field
from typing import List


from packing import (
    create_loading_candidates,
    validate_layout
)


from axles import calculate_axle_weights



@dataclass
class OptimizationResult:

    success: bool

    best: list = field(default_factory=list)

    axle_report: dict = field(default_factory=dict)

    message: str = ""

    rejected: list = field(default_factory=list)



# ==========================================================
# LEGAL CHECK
# ==========================================================


def check_legal(truck, layout):


    errors = []


    valid, physical_errors = validate_layout(
        layout
    )


    if not valid:

        errors.extend(
            physical_errors
        )


    axle_report = calculate_axle_weights(
        truck,
        layout.pallets
    )


    total = axle_report["total"]


    if total > truck.legal_gross:

        errors.append(
            f"Gross weight exceeded ({total:.0f} kg / {truck.legal_gross:.0f} kg)"
        )


    for name, axle in axle_report.items():

        if not isinstance(axle, dict):
            continue


        if axle["weight"] > axle["limit"]:

            errors.append(
                f"{name} exceeded ({axle['weight']:.0f} kg / {axle['limit']:.0f} kg)"
            )


    return (

        len(errors) == 0,

        axle_report,

        errors

    )



# ==========================================================
# BALANCE SCORE
# ==========================================================


def score_layout(layout, axle_report):


    score = 0


    # pallets always first

    score += layout.pallet_count * 100000



    # penalise axle usage

    for name, axle in axle_report.items():

        if not isinstance(axle, dict):
            continue


        utilisation = (

            axle["weight"]

            /

            axle["limit"]

        )


        score -= (

            utilisation ** 4

        ) * 50000



    # prefer shorter loading length

    score -= layout.used_length * 10


    return score



# ==========================================================
# OPTIMIZER
# ==========================================================


def optimize_load(truck, cargo):


    candidates = create_loading_candidates(
        truck,
        cargo
    )


    if not candidates:

        return OptimizationResult(

            False,

            message="No physical loading solution found."

        )



    legal = []

    rejected = []



    for layout in candidates:


        ok, axle_report, errors = check_legal(
            truck,
            layout
        )


        if ok:

            legal.append(

                (
                    layout,
                    axle_report
                )

            )


        else:

            rejected.append(

                {

                    "pallets": layout.pallet_count,

                    "pattern": layout.pattern_name,

                    "reason": "; ".join(errors)

                }

            )



    if not legal:


        return OptimizationResult(

            success=False,

            message="No legal loading solution found.",

            rejected=rejected

        )



    legal.sort(

        key=lambda x:

            score_layout(
                x[0],
                x[1]
            ),

        reverse=True

    )



    layout, axle_report = legal[0]


    return OptimizationResult(

        success=True,

        best=[layout],

        axle_report=axle_report,

        message="Legal loading solution found.",

        rejected=rejected

    )