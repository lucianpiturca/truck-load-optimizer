# ==========================================================
# axles.py
# Truck Load Optimizer
# Axle weight calculation
# ==========================================================


def calculate_cargo_cg(truck, pallets):

    total_weight = sum(
        p.weight for p in pallets
    )

    if total_weight == 0:
        return 0


    moment = 0


    for pallet in pallets:

        # pallet.y is trailer position from front wall
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
# TRAILER LOAD DISTRIBUTION
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


    # distance from kingpin to trailer front
    trailer_front_offset = getattr(
        truck,
        "trailer_front_offset",
        1.60
    )


    # CG distance behind kingpin

    cg_from_kingpin = (
        trailer_front_offset
        +
        cg_from_trailer_front
    )


    bogie_position = getattr(
        truck,
        "bogie_position",
        7.60
    )


    # trailer beam reaction

    bogie_load = (
        cargo_weight
        *
        cg_from_kingpin
        /
        bogie_position
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


    wheelbase = getattr(
        truck,
        "wheelbase",
        3.60
    )


    kingpin_to_drive = getattr(
        truck,
        "kingpin_to_drive_axle",
        0.90
    )


    kingpin_to_steer = (
        wheelbase
        +
        kingpin_to_drive
    )


    steer_load = (
        kingpin_load
        *
        kingpin_to_drive
        /
        kingpin_to_steer
    )


    drive_load = (
        kingpin_load
        -
        steer_load
    )


    return (
        steer_load,
        drive_load
    )



# ==========================================================
# TRIDEM
# ==========================================================


def calculate_tridem_axles(bogie_load):


    axle = bogie_load / 3


    return [

        axle,
        axle,
        axle

    ]



# ==========================================================
# MAIN API
# ==========================================================


def calculate_axle_weights(truck, pallets):


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



    report = {

        "Axle 1": {

            "weight": axle_weights[0],

            "limit": truck.axle_limits[0]

        },


        "Axle 2": {

            "weight": axle_weights[1],

            "limit": truck.axle_limits[1]

        },


        "Axle 3": {

            "weight": axle_weights[2],

            "limit": truck.axle_limits[2]

        },


        "Axle 4": {

            "weight": axle_weights[3],

            "limit": truck.axle_limits[3]

        },


        "Axle 5": {

            "weight": axle_weights[4],

            "limit": truck.axle_limits[4]

        },


        "total": sum(axle_weights),


        "centre_of_gravity": calculate_cargo_cg(
            truck,
            pallets
        ),


        # temporary calibration information

        "debug": {

            "cargo_weight": sum(
                p.weight for p in pallets
            ),

            "kingpin_load": kingpin_load,

            "bogie_load": bogie_load

        }

    }


    return report