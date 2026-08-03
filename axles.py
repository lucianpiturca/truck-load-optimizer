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



    # Distance from kingpin to trailer front

    trailer_front_offset = getattr(

        truck,

        "trailer_front_offset",

        1.60

    )



    # Convert trailer coordinate to kingpin coordinate

    # Kingpin is ahead of trailer front

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



    # Static beam calculation

    bogie_load = (

        cargo_weight

        *

        cg_from_kingpin

        /

        bogie_position

    )



    # Safety boundaries

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



    distance_kingpin_to_steer = (

        wheelbase

        +

        kingpin_to_drive

    )



    steer_load = (

        kingpin_load

        *

        kingpin_to_drive

        /

        distance_kingpin_to_steer

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


    axle_load = (

        bogie_load / 3

    )


    return [

        axle_load,

        axle_load,

        axle_load

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


        "bogie_load": bogie_load


    }



    return report