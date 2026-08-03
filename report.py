# ==========================================================
# report.py
# Truck Load Optimizer
# Text report generator
# ==========================================================


def generate_report(truck, result):


    lines = []


    lines.append("🚛 " + truck.name)

    lines.append("")


    # ======================================================
    # NO SOLUTION
    # ======================================================

    if not result.success:


        lines.append(

            "❌ No legal loading solution found."

        )


        lines.append("")


        if hasattr(result, "message"):

            lines.append(

                result.message

            )


        if hasattr(result, "failures"):


            lines.append("")


            lines.append(

                "Reasons tested:"

            )


            for failure in result.failures:

                lines.append(

                    "- " + failure

                )


        return "\n".join(lines)



    # ======================================================
    # SOLUTION
    # ======================================================


    layout = result.best[0]


    lines.append(

        "📦 Load Summary"

    )


    lines.append(

        f"Loaded pallets: {len(layout.pallets)}"

    )


    lines.append(

        f"Trailer used: {layout.used_length:.2f} m"

    )


    lines.append("")



    # ======================================================
    # AXLES
    # ======================================================


    axle_report = result.best[1]



    lines.append(

        "⚖️ Axle Weight Report"

    )


    for i in range(1, 6):


        axle = axle_report.get(

            f"Axle {i}"

        )


        if axle:


            weight = axle["weight"]

            limit = axle["limit"]


            if weight <= limit:

                status = "🟢"

            else:

                status = "🔴"


            lines.append(

                f"{status} Axle {i}: "

                f"{weight:,.0f} kg / "

                f"{limit:,.0f} kg"

            )



    lines.append("")


    total = axle_report.get(

        "total",

        0

    )


    if total <= truck.legal_gross:

        status = "🟢"

    else:

        status = "🔴"



    lines.append(

        "🚛 Total Weight"

    )


    lines.append(

        f"{status} Total: "

        f"{total:,.0f} kg / "

        f"{truck.legal_gross:,.0f} kg"

    )



    lines.append("")


    cg = axle_report.get(

        "centre_of_gravity",

        0

    )


    lines.append(

        f"📍 Centre of gravity: {cg:.2f} m"

    )



    # ======================================================
    # DEBUG SECTION
    # ======================================================


    debug = axle_report.get(

        "debug"

    )


    if debug:


        lines.append("")

        lines.append(

            "🔧 Axle Calculation Debug"

        )


        lines.append(

            f"Cargo weight: "

            f"{debug.get('cargo_weight',0):,.0f} kg"

        )


        lines.append(

            f"Cargo CG from trailer front: "

            f"{debug.get('cargo_cg_from_trailer_front',0):.2f} m"

        )


        lines.append(

            f"Kingpin load: "

            f"{debug.get('kingpin_load',0):,.0f} kg"

        )


        lines.append(

            f"Bogie load: "

            f"{debug.get('bogie_load',0):,.0f} kg"

        )



    # ======================================================
    # NOT LOADED
    # ======================================================


    if hasattr(layout, "not_loaded") and layout.not_loaded:


        lines.append("")

        lines.append(

            "⚠️ Cargo Not Loaded"

        )


        for item in layout.not_loaded:


            lines.append(

                f"- {item}"

            )



    return "\n".join(lines)