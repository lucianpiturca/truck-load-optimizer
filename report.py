# ==========================================================
# report.py
# Truck Load Optimizer
# ==========================================================


def generate_report(truck, result):

    lines = []

    lines.append(f"TRUCK: {truck.name.upper()}")
    lines.append("")

    # ======================================================
    # SUCCESS
    # ======================================================

    if result.success:

        layout = result.best[0]

        lines.append("LOAD SUMMARY")

        lines.append(
            f"Requested pallets: {result.requested_pallets}"
        )

        lines.append(
            f"Loaded pallets: {result.loaded_pallets}"
        )

        not_loaded = (
            result.requested_pallets
            - result.loaded_pallets
        )

        if not_loaded > 0:

            lines.append("")

            pallet_word = (
                "pallet"
                if not_loaded == 1
                else "pallets"
            )

            lines.append(
                f"NOT LOADED: {not_loaded} {pallet_word}"
            )

            lines.append(
                "Reason: trailer reached its usable loading length."
            )

        lines.append("")

        lines.append(
            f"Trailer used: {layout.used_length:.2f} m"
        )

        lines.append("")

        add_axle_report(
            lines,
            result.axle_report,
            "AXLE WEIGHT REPORT"
        )

        add_total_report(
            lines,
            result.axle_report,
            truck
        )

        add_cg_report(
            lines,
            result.axle_report
        )

        return "\n".join(lines)

    # ======================================================
    # FAILURE
    # ======================================================

    lines.append("NO LEGAL LOADING SOLUTION FOUND.")
    lines.append("")
    lines.append(result.message)

    if result.rejected:

        lines.append("")
        lines.append("Reasons tested:")

        for item in result.rejected:

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
            "FAILED LOAD AXLE CHECK"
        )

        add_total_report(
            lines,
            result.axle_report,
            truck
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
            "OK"
            if weight <= limit
            else "OVER"
        )

        lines.append(
            f"[{icon}] {name}: "
            f"{weight:,.0f} kg / {limit:,.0f} kg"
        )


# ==========================================================
# TOTAL
# ==========================================================


def add_total_report(lines, axle_report, truck):

    total = axle_report.get(
        "total",
        0
    )

    icon = (
        "OK"
        if total <= truck.legal_gross
        else "OVER"
    )

    lines.append("")
    lines.append("TOTAL WEIGHT")
    lines.append(
        f"[{icon}] Total: "
        f"{total:,.0f} kg / "
        f"{truck.legal_gross:,.0f} kg"
    )


# ==========================================================
# CENTRE OF GRAVITY + DEBUG
# ==========================================================


def add_cg_report(lines, axle_report):

    cg = axle_report.get(
        "centre_of_gravity"
    )

    if cg is not None:

        lines.append("")
        lines.append(
            f"Centre of gravity: {cg:.2f} m"
        )

    debug = axle_report.get("debug")

    if debug:

        lines.append("")
        lines.append(
            "AXLE CALCULATION DETAILS"
        )

        for key, value in debug.items():

            if isinstance(value, float):

                value = f"{value:,.2f}"

            lines.append(
                f"{key}: {value}"
            )
