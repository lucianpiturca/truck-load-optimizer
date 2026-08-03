# ==========================================================
# axles.py
# Truck Load Optimizer
# Axle weight calculation
# ==========================================================


# ==========================================================
# CARGO CG
# ==========================================================


def calculate_cargo_cg(truck, pallets):

    total_weight = sum(
        p.weight for p in pallets
    )

    if total_weight == 0:
        return 0


    moment = 0


    for pallet in pallets:

        pallet_center = (
            pallet.y
            +
            pallet.draw_length / 2
        )

        moment += (
            pallet.weight
            *
            pallet_center
        )


    return moment / total_weight



# ==========================================================
# TRAILER REACTIONS
# ==========================================================


def calculate_trailer_reactions(truck, pallets):


    cargo_weight = sum(
        p.weight for p in pallets
    )


    if cargo_weight == 0:

        return 0, 0



    cg_from_trailer_front = calculate_cargo_cg(
        truck,
        pallets
    )


    trailer_front_offset = getattr(
        truck,
        "trailer_front_offset",
        1.60
    )


    # Convert trailer coordinate to kingpin reference

    cg_from_kingpin = (

        cg_from_trailer_front

        -

        trailer_front_offset

    )


    bogie_position = getattr(
        truck,
        "bogie_position",
        7.60
    )


    bogie_load = (

        cargo_weight

        *

        cg_from_kingpin

        /

        bogie_position

    )


    bogie_load = max(
        0,
        min(
            cargo_weight,
            bogie_load
        )
    )


    kingpin_load = (

        cargo_weight

        -

        bogie_load

    )


    return (

        kingpin_load,

        bogie_load

    )



# ==========================================================
# TRACTOR AXLES
# ==========================================================


def calculate_tractor_axles(truck, kingpin_load):


    # Kingpin load distribution
    #
    # European tractor approximation:
    #
    # Steer axle: 10%
    # Drive axle: 90%


    steer_load = (

        kingpin_load

        *

        0.10

    )


    drive_load = (

        kingpin_load

        *

        0.90

    )


    return (

        steer_load,

        drive_load

    )



# ==========================================================
# TRIDEM
# ==========================================================


def calculate_tridem_axles(bogie_load):


    each_axle = (

        bogie_load

        /

        3

    )


    return [

        each_axle,

        each_axle,

        each_axle

    ]



# ==========================================================
# MAIN
# ==========================================================


def calculate_axle_weights(truck, pallets):


    cargo_weight = sum(
        p.weight for p in pallets
    )


    cargo_cg = calculate_cargo_cg(
        truck,
        pallets
    )


    kingpin_load, bogie_load = calculate_trailer_reactions(
        truck,
        pallets
    )


    steer_load, drive_load = calculate_tractor_axles(
        truck,
        kingpin_load
    )


    tridem = calculate_tridem_axles(
        bogie_load
    )


    axle_weights = [

        truck.empty_axles[0] + steer_load,

        truck.empty_axles[1] + drive_load,

        truck.empty_axles[2] + tridem[0],

        truck.empty_axles[3] + tridem[1],

        truck.empty_axles[4] + tridem[2]

    ]



    report = {}



    for i, weight in enumerate(axle_weights):

        report[f"Axle {i+1}"] = {

            "weight": weight,

            "limit": truck.axle_limits[i]

        }



    report["total"] = sum(
        axle_weights
    )


    report["centre_of_gravity"] = cargo_cg


    report["debug"] = {

        "cargo_weight": cargo_weight,

        "cargo_cg_from_trailer_front": cargo_cg,

        "kingpin_load": kingpin_load,

        "bogie_load": bogie_load,

        "steer_transfer_percent": "10%",

        "drive_transfer_percent": "90%"

    }


    return report