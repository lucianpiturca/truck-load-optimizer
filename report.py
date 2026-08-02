# ==========================================================
# report.py
# Truck Load Optimizer
#
# Text report generator
# ==========================================================


from truck import Truck
from optimizer import OptimizationResult



# ==========================================================
# FORMAT HELPERS
# ==========================================================


def weight_status(
    value,
    limit
):

    if value <= limit:

        return "🟢"

    return "🔴"



def metres(value):

    return f"{value:.2f} m"



# ==========================================================
# MAIN REPORT
# ==========================================================


def generate_report(

    truck: Truck,

    result: OptimizationResult

):


    lines = []



    # ------------------------------------------------------
    # Header
    # ------------------------------------------------------


    lines.append(

        f"🚛 {truck.name}"

    )


    lines.append("")



    # ------------------------------------------------------
    # Load summary
    # ------------------------------------------------------


    lines.append(

        "📦 Load Summary"

    )


    lines.append(

        f"Loaded pallets: {len(result.loaded_pallets)}"

    )



    if result.best:


        layout = result.best[0]


        used = layout.used_length


        free = (

            truck.trailer_length

            -

            used

        )


        utilisation = (

            layout.used_area

            /

            (

                truck.trailer_length

                *

                truck.trailer_width

            )

            *

            100

        )



        lines.append(

            f"Trailer used: {metres(used)}"

        )


        lines.append(

            f"Trailer free: {metres(free)}"

        )


        lines.append(

            f"Floor utilisation: {utilisation:.1f} %"

        )



    lines.append("")



    # ------------------------------------------------------
    # Axles
    # ------------------------------------------------------


    if result.axle_report:


        axle = result.axle_report



        lines.append(

            "⚖️ Axle Weight Report"

        )



        for index, value in enumerate(

            axle.axle_weights

        ):


            limit = truck.axle_limits[index]


            icon = weight_status(

                value,

                limit

            )



            extra = ""


            if value > limit:

                extra = " OVERWEIGHT"



            lines.append(

                f"{icon} Axle {index+1}: "

                f"{value:,.0f} kg / "

                f"{limit:,.0f} kg"

                f"{extra}"

            )



        lines.append("")



        lines.append(

            "🚛 Total Weight"

        )



        icon = weight_status(

            axle.total_weight,

            truck.legal_gross

        )



        extra = ""


        if axle.total_weight > truck.legal_gross:

            extra = " OVERWEIGHT"



        lines.append(

            f"{icon} Total: "

            f"{axle.total_weight:,.0f} kg / "

            f"{truck.legal_gross:,.0f} kg"

            f"{extra}"

        )



        lines.append("")



        lines.append(

            f"📍 Centre of gravity: "

            f"{axle.centre_of_gravity:.2f} m"

        )



    # ------------------------------------------------------
    # Rejected cargo
    # ------------------------------------------------------


    lines.append("")



    lines.append(

        "⚠️ Cargo Not Loaded"

    )



    if not result.rejected_pallets:


        lines.append(

            "All cargo was loaded."

        )


    else:


        for pallet in result.rejected_pallets:


            reason = pallet.reason_not_loaded


            if not reason:

                reason = (

                    "Could not fit legally"

                )



            lines.append(

                f"{pallet.description} "

                f"(Pallet {pallet.id}): "

                f"{reason}"

            )



    return "\n".join(lines)