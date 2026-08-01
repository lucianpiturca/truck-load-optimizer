# report.py

from axles import AxleReport
from packing import LayoutResult
from cargo import Pallet



# ==========================================================
# AXLE REPORT TEXT
# ==========================================================


def axle_status_icon(overloaded):

    if overloaded:
        return "🔴"

    return "🟢"



def total_status_icon(legal):

    if legal:
        return "🟢"

    return "🔴"



def generate_axle_report(

    report: AxleReport

):

    lines = []


    lines.append(

        "## ⚖️ Axle Weight Report"

    )


    for axle in report.axles:


        icon = axle_status_icon(

            axle.overloaded

        )


        if axle.overloaded:

            text = (

                f"{icon} **Axle {axle.axle_number}:** "

                f"{axle.weight:,.0f} kg / "

                f"{axle.limit:,.0f} kg "

                "**OVERWEIGHT**"

            )

        else:

            text = (

                f"{icon} **Axle {axle.axle_number}:** "

                f"{axle.weight:,.0f} kg / "

                f"{axle.limit:,.0f} kg"

            )


        lines.append(text)



    lines.append("")



    total_icon = total_status_icon(

        report.legal_total

    )


    if report.legal_total:


        lines.append(

            f"## 🚛 Total Weight\n\n"

            f"{total_icon} **Total: "

            f"{report.total_weight:,.0f} kg / "

            f"40,000 kg**"

        )


    else:


        lines.append(

            f"## 🚛 Total Weight\n\n"

            f"{total_icon} **Total: "

            f"{report.total_weight:,.0f} kg / "

            f"40,000 kg "

            "OVERWEIGHT**"

        )



    lines.append("")


    lines.append(

        f"📍 Centre of gravity: "

        f"{report.centre_of_gravity:.2f} m"

    )


    return "\n\n".join(lines)




# ==========================================================
# LOAD SUMMARY
# ==========================================================


def generate_load_summary(

    layout: LayoutResult

):


    pallets = len(

        layout.pallets

    )


    return f"""
## 📦 Load Summary

**Loaded pallets:** {pallets}

**Trailer used:** {layout.used_length:.2f} m

**Trailer free:** {layout.free_length:.2f} m

**Floor utilisation:** {layout.utilisation*100:.1f} %
"""



# ==========================================================
# REJECTED CARGO
# ==========================================================


def generate_rejected_report(

    rejected: list[Pallet]

):


    if not rejected:

        return (

            "## ✅ Cargo Not Loaded\n\n"

            "All cargo was loaded."

        )



    text = [

        "## ⚠️ Cargo Not Loaded"

    ]


    for pallet in rejected:


        reason = pallet.reject_reason


        if not reason:

            reason = (

                "Could not fit legally"

            )


        text.append(

            f"- {pallet.description} "

            f"(Pallet {pallet.id}): "

            f"{reason}"

        )



    return "\n".join(text)



# ==========================================================
# FULL REPORT
# ==========================================================


def generate_full_report(

    layout,

    axle_report,

    rejected

):


    sections = []


    sections.append(

        generate_load_summary(

            layout

        )

    )


    sections.append(

        generate_axle_report(

            axle_report

        )

    )


    sections.append(

        generate_rejected_report(

            rejected

        )

    )


    return "\n\n---\n\n".join(

        sections

    )