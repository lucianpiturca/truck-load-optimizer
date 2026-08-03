# ==========================================================
# axles.py
# Truck Load Optimizer
# Static beam axle calculation
# ==========================================================


# Trailer geometry
KINGPIN_TO_BOGIE_CENTER = 7.7
FRONT_OVERHANG = 1.6



# ==========================================================
# PALLET POSITION
# ==========================================================

def pallet_position_from_kingpin(pallet):

    pallet_center = (
        pallet.y
        +
        pallet.draw_length / 2
    )

    return (
        pallet_center
        -
        FRONT_OVERHANG
    )



# ==========================================================
# TRAILER BEAM CALCULATION
# ==========================================================

def calculate_trailer_loads(pallets):


    kingpin_load = 0

    bogie_load = 0


    debug_pallets = []



    for pallet in pallets:


        x = pallet_position_from_kingpin(
            pallet
        )


        weight = pallet.weight



        kingpin_force = (

            weight

            *

            (

                KINGPIN_TO_BOGIE_CENTER

                -

                x

            )

            /

            KINGPIN_TO_BOGIE_CENTER

        )



        bogie_force = (

            weight

            *

            x

            /

            KINGPIN_TO_BOGIE_CENTER

        )



        kingpin_load += kingpin_force

        bogie_load += bogie_force



        debug_pallets.append(

            {

                "position_from_kingpin": x,

                "weight": weight,

                "kingpin_force": kingpin_force,

                "bogie_force": bogie_force

            }

        )



    # Physical constraint:
    # fifth wheel cannot have negative load

    if kingpin_load < 0:

        bogie_load += kingpin_load

        kingpin_load = 0



    return (

        kingpin_load,

        bogie_load,

        debug_pallets

    )



# ==========================================================
# TRACTOR AXLES
# ==========================================================

def calculate_tractor_axles(truck, kingpin_load):


    kingpin_load = max(
        0,
        kingpin_load
    )


    steer_transfer = (

        kingpin_load

        *

        0.10

    )


    drive_transfer = (

        kingpin_load

        *

        0.90

    )


    return (

        steer_transfer,

        drive_transfer

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
# MAIN AXLE CALCULATION
# ==========================================================

def calculate_axle_weights(truck, pallets):


    cargo_weight = sum(

        p.weight for p in pallets

    )


    kingpin_load, bogie_load, debug_pallets = calculate_trailer_loads(

        pallets

    )



    steer_transfer, drive_transfer = calculate_tractor_axles(

        truck,

        kingpin_load

    )



    tridem = calculate_tridem_axles(

        bogie_load

    )



    axle_weights = [

        truck.empty_axles[0] + steer_transfer,

        truck.empty_axles[1] + drive_transfer,

        truck.empty_axles[2] + tridem[0],

        truck.empty_axles[3] + tridem[1],

        truck.empty_axles[4] + tridem[2]

    ]



    report = {}



    for index, weight in enumerate(axle_weights):


        report[f"Axle {index+1}"] = {

            "weight": weight,

            "limit": truck.axle_limits[index]

        }



    report["total"] = sum(

        axle_weights

    )



    if cargo_weight > 0:


        cg = sum(

            pallet_position_from_kingpin(p)

            *

            p.weight

            for p in pallets

        ) / cargo_weight


    else:

        cg = 0



    report["centre_of_gravity"] = cg



    report["debug"] = {

        "cargo_weight": cargo_weight,

        "kingpin_load": kingpin_load,

        "bogie_load": bogie_load,

        "kingpin_to_bogie_center": KINGPIN_TO_BOGIE_CENTER,

        "front_overhang": FRONT_OVERHANG,

        "pallet_count": len(pallets)

    }



    return report