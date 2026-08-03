# ==========================================================
# axles.py
# Truck Load Optimizer
# Axle weight calculation
# ==========================================================



def get_value(obj, name, default):

    return getattr(
        obj,
        name,
        default
    )



# ==========================================================
# CARGO POSITION
# ==========================================================


def pallet_position_from_kingpin(

    truck,

    pallet

):

    """
    Position of pallet centre measured
    from the kingpin.

    """

    trailer_front_offset = get_value(

        truck,

        "trailer_front_offset",

        1.60

    )


    return (

        trailer_front_offset

        +

        pallet.y

        +

        pallet.draw_length / 2

    )



# ==========================================================
# CARGO CG
# ==========================================================


def calculate_cargo_cg(

    truck,

    pallets

):


    total_weight = sum(

        p.weight

        for p in pallets

    )


    if total_weight == 0:

        return 0



    moment = 0



    for pallet in pallets:


        position = pallet_position_from_kingpin(

            truck,

            pallet

        )


        moment += (

            pallet.weight

            *

            position

        )



    return moment / total_weight



# ==========================================================
# TRAILER LOAD DISTRIBUTION
# ==========================================================


def calculate_trailer_reactions(

    truck,

    pallets

):


    cargo_weight = sum(

        p.weight

        for p in pallets

    )


    if cargo_weight == 0:

        return 0, 0



    cg = calculate_cargo_cg(

        truck,

        pallets

    )


    bogie_position = get_value(

        truck,

        "bogie_position",

        7.60

    )



    bogie_load = (

        cargo_weight

        *

        cg

        /

        bogie_position

    )


    kingpin_load = (

        cargo_weight

        -

        bogie_load

    )



    # prevent impossible values

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


def calculate_tractor_axles(

    truck,

    kingpin_load

):

    """

    Fifth wheel load transfer.

    Uses:

    - wheelbase
    - kingpin_to_drive_axle


    """



    wheelbase = get_value(

        truck,

        "wheelbase",

        3.60

    )


    kingpin_to_drive = get_value(

        truck,

        "kingpin_to_drive_axle",

        0.90

    )


    # distance kingpin to steer axle

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
# TRAILER AXLES
# ==========================================================


def calculate_tridem_axles(

    bogie_load

):


    each = (

        bogie_load / 3

    )


    return [

        each,

        each,

        each

    ]



# ==========================================================
# MAIN FUNCTION
# ==========================================================


def calculate_axle_weights(

    truck,

    pallets

):


    kingpin_load, bogie_load = calculate_trailer_reactions(

        truck,

        pallets

    )


    # temporary diagnostics

    print(

        "DEBUG KINGPIN:",

        round(kingpin_load, 1)

    )


    print(

        "DEBUG BOGIE:",

        round(bogie_load, 1)

    )


    print(

        "DEBUG CG:",

        round(

            calculate_cargo_cg(

                truck,

                pallets

            ),

            2

        )

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


    report["centre_of_gravity"] = calculate_cargo_cg(

        truck,

        pallets

    )


    return report