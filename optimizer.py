# ==========================================================
# optimizer.py
# Truck Load Optimizer
# Advanced optimisation engine
# ==========================================================


from dataclasses import dataclass, field

from typing import List


from packing import (

    create_loading_candidates,

    validate_layout

)


from axles import calculate_axle_weights




# ==========================================================
# RESULT OBJECT
# ==========================================================


@dataclass
class OptimizationResult:


    success: bool


    best: list = field(

        default_factory=list

    )


    axle_report: dict = field(

        default_factory=dict

    )


    message: str = ""


    rejected: list = field(

        default_factory=list

    )





# ==========================================================
# LEGAL CHECK
# ==========================================================


def check_legal(

    truck,

    layout

):


    errors = []



    # -------------------------
    # Physical validation
    # -------------------------

    valid, physical_errors = validate_layout(

        layout

    )


    if not valid:

        errors.extend(

            physical_errors

        )



    # -------------------------
    # Gross weight
    # -------------------------

    axle_report = calculate_axle_weights(

        truck,

        layout.pallets

    )



    total_weight = axle_report["total"]



    if total_weight > truck.legal_gross:


        errors.append(

            f"Gross weight exceeded "

            f"({total_weight:.0f} kg / "

            f"{truck.legal_gross:.0f} kg)"

        )



    # -------------------------
    # Axles
    # -------------------------

    for axle_name, axle in axle_report.items():


        if axle_name == "total":

            continue


        if axle["weight"] > axle["limit"]:


            errors.append(

                f"{axle_name} exceeded "

                f"({axle['weight']:.0f} kg / "

                f"{axle['limit']:.0f} kg)"

            )



    return (

        len(errors) == 0,

        axle_report,

        errors

    )





# ==========================================================
# LAYOUT SCORE
# ==========================================================


def optimisation_score(

    layout

):


    score = 0



    # Primary objective:
    # load as many pallets as possible

    score += layout.pallet_count * 100000



    # Prefer full trailer utilisation

    score += (

        layout.used_length * 100

    )



    # Prefer Euro 3-wide

    if layout.pattern_name == "EURO-3":

        score += 50000



    return score





# ==========================================================
# MAIN OPTIMIZER
# ==========================================================


def optimize_load(

    truck,

    cargo

):


    candidates = create_loading_candidates(

        truck,

        cargo

    )



    if not candidates:


        return OptimizationResult(

            success=False,

            message="No physical loading solution found."

        )



    legal_solutions = []

    rejected = []



    for layout in candidates:



        legal, axle_report, errors = check_legal(

            truck,

            layout

        )



        if legal:


            layout.score = optimisation_score(

                layout

            )


            legal_solutions.append(

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





    # ------------------------------------------------------
    # No legal solution
    # ------------------------------------------------------

    if not legal_solutions:



        return OptimizationResult(

            success=False,

            message=(

                "No legal loading solution found."

            ),

            rejected=rejected

        )





    # ------------------------------------------------------
    # Select best
    # ------------------------------------------------------

    legal_solutions.sort(

        key=lambda x:

            optimisation_score(x[0]),

        reverse=True

    )



    best_layout, best_axle = legal_solutions[0]



    return OptimizationResult(

        success=True,

        best=[best_layout],

        axle_report=best_axle,

        message="Legal loading solution found."

    )