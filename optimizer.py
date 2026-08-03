# ==========================================================
# optimizer.py
# Truck Load Optimizer
# ==========================================================


from dataclasses import dataclass, field


from packing import (
    create_loading_candidates,
    validate_layout
)


from axles import calculate_axle_weights



# ==========================================================
# RESULT
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



    # ------------------------------------------------------
    # Physical validation
    # ------------------------------------------------------


    valid, physical_errors = validate_layout(

        layout

    )


    if not valid:


        errors.extend(

            physical_errors

        )



    # ------------------------------------------------------
    # Axles
    # ------------------------------------------------------


    axle_report = calculate_axle_weights(

        truck,

        layout.pallets

    )



    # ------------------------------------------------------
    # Gross
    # ------------------------------------------------------


    total_weight = axle_report.get(

        "total",

        0

    )


    if total_weight > truck.legal_gross:


        errors.append(

            f"Gross weight exceeded "

            f"({total_weight:.0f} kg / "

            f"{truck.legal_gross:.0f} kg)"

        )



    # ------------------------------------------------------
    # Axle limits
    # ------------------------------------------------------


    for axle_name, axle in axle_report.items():


        if not isinstance(

            axle,

            dict

        ):

            continue



        if (

            "weight" not in axle

            or

            "limit" not in axle

        ):

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
# SCORE
# ==========================================================


def score_layout(

    layout,

    axle_report

):


    score = 0



    # Most important:
    # maximum pallets


    score += (

        layout.pallet_count

        *

        100000

    )



    # Axle balance penalty


    for name, axle in axle_report.items():


        if not isinstance(

            axle,

            dict

        ):

            continue



        if (

            "weight" not in axle

            or

            "limit" not in axle

        ):

            continue



        utilisation = (

            axle["weight"]

            /

            axle["limit"]

        )



        # Avoid loads close to axle limits

        score -= (

            utilisation ** 4

            *

            50000

        )



    # Prefer compact loading


    score -= (

        layout.used_length

        *

        10

    )



    return score



# ==========================================================
# OPTIMIZER
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



    # ------------------------------------------------------
    # No legal solution
    # ------------------------------------------------------


    if not legal:


        return OptimizationResult(

            success=False,

            message="No legal loading solution found.",

            rejected=rejected

        )



    # ------------------------------------------------------
    # Best solution
    # ------------------------------------------------------


    legal.sort(

        key=lambda item:

            score_layout(

                item[0],

                item[1]

            ),

        reverse=True

    )



    best_layout, best_axles = legal[0]



    return OptimizationResult(

        success=True,

        best=[best_layout],

        axle_report=best_axles,

        message="Legal loading solution found.",

        rejected=rejected

    )