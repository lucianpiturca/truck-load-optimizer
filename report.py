# ==========================================================
# report.py
# Truck Load Optimizer
# Report generator
# ==========================================================



def generate_report(truck, result):


    lines = []


    lines.append(

        "🚛 " + truck.name

    )


    lines.append("")



    # ======================================================
    # FAILURE REPORT
    # ======================================================


    if not result.success:


        lines.append(

            "❌ No legal loading solution found."

        )


        lines.append("")


        lines.append(

            result.message

        )



        failed = getattr(

            result,

            "failed_axle_report",

            {}

        )


        if failed:


            lines.append("")

            lines.append(

                "⚖️ Failed Load Axle Check"

            )



            for i in range(1, 6):


                axle = failed.get(

                    f"Axle {i}"

                )


                if axle:


                    weight = axle.get(

                        "weight",

                        0

                    )


                    limit = axle.get(

                        "limit",

                        0

                    )


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


            lines.append(

                "🚛 Total Weight"

            )


            lines.append(

                f"{failed.get('total',0):,.0f} kg / "

                f"{truck.legal_gross:,.0f} kg"

            )



            if "centre_of_gravity" in failed:


                lines.append("")


                lines.append(

                    f"📍 Centre of gravity: "

                    f"{failed['centre_of_gravity']:.2f} m"

                )



            debug = failed.get(

                "debug"

            )


            if debug:


                lines.append("")

                lines.append(

                    "🔧 Axle Calculation Debug"

                )


                for key, value in debug.items():


                    if isinstance(value, float):

                        lines.append(

                            f"{key}: {value:,.2f}"

                        )

                    else:

                        lines.append(

                            f"{key}: {value}"

                        )



        rejected = getattr(

            result,

            "rejected",

            []

        )


        if rejected:


            lines.append("")

            lines.append(

                "Reasons tested:"

            )


            for item in rejected:


                lines.append(

                    "- "

                    f"{item['pallets']} pallets "

                    f"({item['pattern']}): "

                    f"{item['reason']}"

                )



        return "\n".join(lines)



    # ======================================================
    # SUCCESS REPORT
    # ======================================================


    lines.append(

        "📦 Load Summary"

    )



    if result.best:


        layout = result.best[0]


        lines.append(

            f"Loaded pallets: "

            f"{layout.pallet_count}"

        )


        lines.append(

            f"Trailer used: "

            f"{layout.used_length:.2f} m"

        )



    lines.append("")



    axle_report = (

        result.axle_report

        if result.axle_report

        else result.best[1]

    )



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


    lines.append(

        f"📍 Centre of gravity: "

        f"{axle_report.get('centre_of_gravity',0):.2f} m"

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

                lines.append(

                    f"{key}: {value:,.2f}"

                )

            else:

                lines.append(

                    f"{key}: {value}"

                )



    return "\n".join(lines)