# report.py
# Truck Load Optimizer 2.0
#
# Reporting functions


from optimizer import OptimizationResult
from truck import Truck
from packing import Layout



# ==========================================================
# STATUS ICONS
# ==========================================================


def status_icon(
    value,
    limit
):

    if value <= limit:

        return "🟢"

    return "🔴"



# ==========================================================
# LOAD SUMMARY
# ==========================================================


def load_summary(
    truck: Truck,
    layout: Layout
):

    if layout is None:

        return {
            "loaded": 0,
            "used_length": 0,
            "free_length": truck.internal_length,
            "utilisation": 0
        }


    used = layout.used_length


    free = (

        truck.internal_length

        -

        used

    )


    if free < 0:

        free = 0



    utilisation = (

        layout.used_area

        /

        (
            truck.internal_length
            *
            truck.internal_width
        )

        *

        100

    )



    return {

        "loaded": layout.pallet_count,

        "used_length": used,

        "free_length": free,

        "utilisation": utilisation

    }



# ==========================================================
# STREAMLIT REPORT
# ==========================================================


def generate_report(
    result: OptimizationResult,
    truck: Truck
):


    lines = []



    # ------------------------------------------------------
    # No solution
    # ------------------------------------------------------

    if result.best is None:


        lines.append(

            "❌ No legal loading solution found."

        )


        if result.rejected:


            lines.append(

                ""

            )


            lines.append(

                "Cargo that could not be loaded:"

            )


            for pallet in result.rejected:


                lines.append(

                    f"- {pallet.description}: "
                    f"{pallet.reason_not_loaded}"

                )


        return "\n\n".join(lines)



    layout = result.best



    # ------------------------------------------------------
    # Load summary
    # ------------------------------------------------------

    summary = load_summary(

        truck,

        layout

    )



    lines.append(

        "📦 Load Summary"

    )


    lines.append(

        f"Loaded pallets: "
        f"{summary['loaded']}"

    )


    lines.append(

        f"Trailer used: "
        f"{summary['used_length']:.2f} m"

    )


    lines.append(

        f"Trailer free: "
        f"{summary['free_length']:.2f} m"

    )


    lines.append(

        f"Floor utilisation: "
        f"{summary['utilisation']:.1f} %"

    )



    # ------------------------------------------------------
    # Axles
    # ------------------------------------------------------

    lines.append("")

    lines.append(

        "⚖️ Axle Weight Report"

    )



    axle_report = result.axle_report



    if axle_report:


        for index, weight in enumerate(

            axle_report.axle_weights

        ):


            limit = truck.axle_limits[index]


            icon = status_icon(

                weight,

                limit

            )


            extra = ""


            if weight > limit:

                extra = " OVERWEIGHT"



            lines.append(

                f"{icon} Axle {index+1}: "
                f"{weight:,.0f} kg / "
                f"{limit:,.0f} kg"
                f"{extra}"

            )



        lines.append("")


        icon = status_icon(

            axle_report.total_weight,

            truck.legal_gross

        )


        extra = ""


        if axle_report.total_weight > truck.legal_gross:

            extra = " OVERWEIGHT"



        lines.append(

            "🚛 Total Weight"

        )


        lines.append(

            f"{icon} Total: "
            f"{axle_report.total_weight:,.0f} kg / "
            f"{truck.legal_gross:,.0f} kg"
            f"{extra}"

        )


        lines.append("")


        lines.append(

            f"📍 Centre of gravity: "
            f"{axle_report.centre_of_gravity:.2f} m"

        )



    # ------------------------------------------------------
    # Rejected cargo
    # ------------------------------------------------------

    lines.append("")


    if result.rejected:


        lines.append(

            "⚠️ Cargo Not Loaded"

        )


        for pallet in result.rejected:


            lines.append(

                f"{pallet.description} "
                f"(Pallet {pallet.id}): "
                f"{pallet.reason_not_loaded}"

            )



    else:


        lines.append(

            "✅ Cargo Not Loaded"

        )


        lines.append(

            "All cargo was loaded."

        )



    return "\n\n".join(lines)