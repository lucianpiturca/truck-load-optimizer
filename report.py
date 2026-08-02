# report.py
# Truck Load Optimizer 2.0

from optimizer import OptimizationResult
from truck import Truck
from packing import Layout



def status_icon(value, limit):

    if value <= limit:
        return "🟢"

    return "🔴"



def load_summary(truck, layout):

    if layout is None:

        return {
            "loaded": 0,
            "used_length": 0,
            "free_length": truck.trailer_length,
            "utilisation": 0
        }


    used = layout.used_length


    free = truck.trailer_length - used


    if free < 0:
        free = 0


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


    return {

        "loaded": layout.pallet_count,

        "used_length": used,

        "free_length": free,

        "utilisation": utilisation

    }



def generate_report(
    result: OptimizationResult,
    truck: Truck
):


    lines = []


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



    summary = load_summary(

        truck,

        layout

    )



    lines.append(
        "📦 Load Summary"
    )


    lines.append(

        f"Loaded pallets: {summary['loaded']}"

    )


    lines.append(

        f"Trailer used: {summary['used_length']:.2f} m"

    )


    lines.append(

        f"Trailer free: {summary['free_length']:.2f} m"

    )


    lines.append(

        f"Floor utilisation: {summary['utilisation']:.1f} %"

    )



    lines.append("")

    lines.append(
        "⚖️ Axle Weight Report"
    )



    axle_report = result.axle_report



    if axle_report:


        for i, weight in enumerate(

            axle_report.axle_weights

        ):


            limit = truck.axle_limits[i]


            icon = status_icon(

                weight,

                limit

            )


            extra = ""

            if weight > limit:

                extra = " OVERWEIGHT"


            lines.append(

                f"{icon} Axle {i+1}: "
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