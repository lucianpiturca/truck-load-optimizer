# ==========================================================
# report.py
# Truck Load Optimizer
# Reporting engine
# ==========================================================


def kg(value):

    return f"{value:,.0f} kg"



def generate_report(

    truck,

    result

):

    lines = []


    # ======================================================
    # Header
    # ======================================================

    lines.append(

        f"🚛 {truck.name}"

    )

    lines.append("")



    # ======================================================
    # No solution
    # ======================================================

    if not result.success:


        lines.append(

            "❌ No legal loading solution found."

        )

        lines.append("")


        if result.rejected:


            lines.append(

                "Reasons tested:"

            )


            for item in result.rejected[:10]:

                lines.append(

                    f"- {item['pallets']} pallets "

                    f"({item['pattern']}): "

                    f"{item['reason']}"

                )


        return "\n".join(lines)



    # ======================================================
    # Layout
    # ======================================================

    layout = result.best[0]


    lines.append(

        "📦 Load Summary"

    )


    lines.append(

        f"Loaded pallets: {layout.pallet_count}"

    )


    lines.append(

        f"Trailer used: {layout.used_length:.2f} m"

    )


    lines.append(

        f"Trailer free: {layout.free_length:.2f} m"

    )



    utilisation = (

        layout.used_length

        /

        layout.trailer_length

        *

        100

    )


    lines.append(

        f"Floor utilisation: {utilisation:.1f} %"

    )


    lines.append("")



    # ======================================================
    # Axles
    # ======================================================

    lines.append(

        "⚖️ Axle Weight Report"

    )


    axle_report = result.axle_report



    for key, axle in axle_report.items():


        if key == "total":

            continue



        weight = axle["weight"]

        limit = axle["limit"]



        if weight <= limit:

            status = "🟢"

            text = ""

        else:

            status = "🔴"

            text = " OVERWEIGHT"



        lines.append(

            f"{status} {key}: "

            f"{kg(weight)} / "

            f"{kg(limit)}"

            f"{text}"

        )


    lines.append("")



    # ======================================================
    # Total weight
    # ======================================================


    total = axle_report["total"]


    lines.append(

        "🚛 Total Weight"

    )


    if total <= truck.legal_gross:

        status = "🟢"

        warning = ""

    else:

        status = "🔴"

        warning = " OVERWEIGHT"



    lines.append(

        f"{status} Total: "

        f"{kg(total)} / "

        f"{kg(truck.legal_gross)}"

        f"{warning}"

    )


    lines.append("")



    # ======================================================
    # Centre of gravity
    # ======================================================


    if "centre_of_gravity" in axle_report:


        lines.append(

            f"📍 Centre of gravity: "

            f"{axle_report['centre_of_gravity']:.2f} m"

        )


        lines.append("")



    # ======================================================
    # Pattern information
    # ======================================================


    if layout.pattern_name:


        lines.append(

            f"📐 Loading pattern: "

            f"{layout.pattern_name}"

        )


        lines.append("")



    # ======================================================
    # Rejected cargo
    # ======================================================


    if result.rejected:


        lines.append(

            "⚠️ Alternative layouts rejected"

        )


        for item in result.rejected[:5]:

            lines.append(

                f"- {item['pallets']} pallets: "

                f"{item['reason']}"

            )



    return "\n".join(lines)