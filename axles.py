# ==========================================================
# axles.py
# Truck Load Optimizer
# Static beam axle calculation
# ==========================================================


# ==========================================================
# PALLET POSITION
# ==========================================================

def pallet_position_from_kingpin(truck, pallet):

    pallet_center = (
        pallet.y
        +
        pallet.draw_length / 2
    )

    return (
        pallet_center
        -
        truck.trailer_front_offset
    )



# ==========================================================
# TRAILER BEAM CALCULATION
# ==========================================================

def calculate_trailer_loads(truck, pallets):


    kingpin_load = 0

    bogie_load = 0


    debug_pallets = []



    for pallet in pallets:


        x = pallet_position_from_kingpin(

            truck,

            pallet
        )


        weight = pallet.weight



        kingpin_force = (

            weight

            *

            (

                truck.bogie_position

                -

                x

            )

            /

            truck.bogie_position

        )



        bogie_force = (

            weight

            *

            x

            /

            truck.bogie_position

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



    # Keep the reactions signed.  A pallet behind the bogie centre creates a
    # negative *incremental* kingpin reaction and transfers more than its own
    # weight to the bogie.  When added to the measured empty axle weights this
    # is the correct static lever behaviour.



    return (

        kingpin_load,

        bogie_load,

        debug_pallets

    )



# ==========================================================
# TRACTOR AXLES
# ==========================================================

def calculate_tractor_axles(truck, kingpin_load):
    if not 0 <= truck.kingpin_to_drive_axle <= truck.wheelbase:

        raise ValueError(
            "Fifth wheel must be positioned between the steer and drive axles"
        )

    # Static point-load reactions for a two-axle tractor.  The fifth wheel
    # position is vehicle-specific; for the configured 0.60 / 3.60 m
    # geometry this is the agreed 1/6 steer, 5/6 drive split.
    steer_fraction = truck.kingpin_steer_fraction

    steer_transfer = kingpin_load * steer_fraction

    drive_transfer = kingpin_load * (1 - steer_fraction)


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

        truck,

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

            pallet_position_from_kingpin(truck, p)

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

        "kingpin_to_bogie_center": truck.bogie_position,

        "front_overhang": truck.trailer_front_offset,

        "kingpin_to_rear_bulkhead": truck.kingpin_to_rear_bulkhead,

        "kingpin_steer_fraction": truck.kingpin_steer_fraction,

        "pallet_count": len(pallets)

    }



    return report
