# ==========================================================
# report.py
# Truck Load Optimizer
# ==========================================================


def generate_report(truck, result):


    lines = []


    lines.append(
        f"🚛 {truck.name}"
    )


    lines.append("")



    # ======================================================
    # SUCCESS
    # ======================================================


    if result.success:


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


        lines.append("")



        add_axle_report(

            lines,

            result.axle_report,

            "⚖️ Axle Weight Report"

        )


        add_total_report(

            lines,

            result.axle_report

        )


        add_cg_report(

            lines,

            result.axle_report

        )


        # --------------------------------------------------
        # Rejected alternatives
        # --------------------------------------------------


        if result.rejected:


            lines.append("")

            lines.append(

                "⚠️ Other tested loads"

            )


            for item in result.rejected[:5]:


                lines.append(

                    f"- {item['pallets']} pallets "

                    f"({item['pattern']}): "

                    f"{item['reason']}"

                )



        return "\n".join(lines)



    # ======================================================
    # FAILURE
    # ======================================================


    lines.append(

        "❌ No legal loading solution found."

    )


    lines.append("")


    lines.append(

        result.message

    )



    if result.rejected:


        lines.append("")

        lines.append(

            "Reasons tested:"

        )


        for item in result.rejected[:10]:


            lines.append(

                f"- {item['pallets']} pallets "

                f"({item['pattern']}): "

                f"{item['reason']}"

            )



    if result.axle_report:


        lines.append("")


        add_axle_report(

            lines,

            result.axle_report,

            "⚖️ Failed Load Axle Check"

        )


        add_total_report(

            lines,

            result.axle_report

        )


        add_cg_report(

            lines,

            result.axle_report

        )


    return "\n".join(lines)




# ==========================================================
# AXLES
# ==========================================================


def add_axle_report(lines, axle_report, title):


    lines.append(title)



    for name, axle in axle_report.items():


        if not isinstance(axle, dict):

            continue


        if (

            "weight" not in axle

            or

            "limit" not in axle

        ):

            continue



        weight = axle["weight"]

        limit = axle["limit"]



        icon = (

            "🟢"

            if weight <= limit

            else

            "🔴"

        )



        lines.append(

            f"{icon} {name}: "

            f"{weight:,.0f} kg / "

            f"{limit:,.0f} kg"

        )




# ==========================================================
# TOTAL
# ==========================================================


def add_total_report(lines, axle_report):


    total = axle_report.get(

        "total",

        0

    )


    lines.append("")

    lines.append(

        "🚛 Total Weight"

    )


    icon = (

        "🟢"

        if total <= 40000

        else

        "🔴"

    )


    lines.append(

        f"{icon} Total: "

        f"{total:,.0f} kg / "

        f"40,000 kg"

    )




# ==========================================================
# CG + DEBUG
# ==========================================================


def add_cg_report(lines, axle_report):


    cg = axle_report.get(

        "centre_of_gravity"

    )


    if cg is not None:


        lines.append("")


        lines.append(

            f"📍 Centre of gravity: {cg:.2f} m"

        )



    debug = axle_report.get(

        "debug"

    )


    if debug:


        lines.append("")

        lines.append(

            "🔧 Axle Calculation Debug"

        )


        for key, value in debug.items():


            if isinstance(value, float):

                value = f"{value:,.2f}"


            lines.append(

                f"{key}: {value}"

            )